"""
Evolve Consciousness Engine - Simplified Backend
Clean implementation with core RAG functionality
Updated: December 22, 2025
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import os
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
from openai import OpenAI
from anthropic import Anthropic
import re
import time

# Load environment variables
load_dotenv()

# Initialize API clients
pinecone_client = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# Configuration
INDEX_NAME = "consciousness-rag"
EMBEDDING_MODEL = "text-embedding-3-large"
EMBEDDING_DIMENSION = 3072
CHUNK_SIZE = 1800  # Optimal for long documents
CHUNK_OVERLAP = 200

# Initialize Pinecone index
try:
    if INDEX_NAME not in [index.name for index in pinecone_client.list_indexes()]:
        pinecone_client.create_index(
            name=INDEX_NAME,
            dimension=EMBEDDING_DIMENSION,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1")
        )
        time.sleep(10)  # Wait for index to be ready
    index = pinecone_client.Index(INDEX_NAME)
except Exception as e:
    print(f"Pinecone initialization error: {e}")
    index = None

# Initialize FastAPI
app = FastAPI(title="Evolve Consciousness Engine")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")


# ============================================================================
# MODELS
# ============================================================================

class UploadRequest(BaseModel):
    text: str
    title: str
    source: str
    metadata: Optional[Dict[str, Any]] = None


class QueryRequest(BaseModel):
    question: str
    filters: Optional[Dict[str, Any]] = None
    top_k: Optional[int] = 5


class DeleteRequest(BaseModel):
    title: str


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    """
    Split text into overlapping chunks.
    Uses sentence boundaries when possible.
    """
    # Split into sentences
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        # If adding this sentence would exceed chunk size, save current chunk
        if len(current_chunk) + len(sentence) > chunk_size and current_chunk:
            chunks.append(current_chunk.strip())
            # Start new chunk with overlap
            words = current_chunk.split()
            overlap_text = " ".join(words[-50:]) if len(words) > 50 else current_chunk
            current_chunk = overlap_text + " " + sentence
        else:
            current_chunk += " " + sentence
    
    # Add final chunk
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
    
    return chunks


def generate_embedding(text: str) -> List[float]:
    """Generate embedding using OpenAI."""
    try:
        response = openai_client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Embedding generation failed: {str(e)}")


def generate_tags(text: str) -> Dict[str, Any]:
    """
    Generate comprehensive keyword-based tags.
    This is the original 305-line tagging system from expanded-tagging-v2.py
    """
    from tagging import generate_tags as generate_tags_comprehensive
    return generate_tags_comprehensive(text)


def query_claude(prompt: str, context: str) -> str:
    """Query Claude for RAG response."""
    try:
        full_prompt = f"""You are the Evolve Consciousness Engine, an expert in consciousness, mysticism, subtle energy, quantum physics, and addiction recovery as a spiritual path.

Context from knowledge base:
{context}

User question: {prompt}

Provide a comprehensive, insightful answer that synthesizes the context and makes connections across traditions when relevant."""

        response = anthropic_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[{"role": "user", "content": full_prompt}]
        )
        
        return response.content[0].text
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Claude query failed: {str(e)}")


# ============================================================================
# ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint - serve frontend."""
    return FileResponse("static/index.html")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    pinecone_status = "connected" if index is not None else "disconnected"
    
    try:
        stats = index.describe_index_stats() if index else {}
        vector_count = stats.get('total_vector_count', 0)
    except:
        vector_count = 0
    
    return {
        "status": "healthy",
        "pinecone": pinecone_status,
        "vector_count": vector_count,
        "chunk_size": CHUNK_SIZE,
        "embedding_model": EMBEDDING_MODEL
    }


@app.get("/stats")
async def get_stats():
    """Get database statistics."""
    if not index:
        raise HTTPException(status_code=500, detail="Pinecone not initialized")
    
    try:
        stats = index.describe_index_stats()
        return {
            "total_vectors": stats.get('total_vector_count', 0),
            "dimension": EMBEDDING_DIMENSION,
            "chunk_size": CHUNK_SIZE,
            "index_name": INDEX_NAME
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")


@app.get("/documents")
async def list_documents():
    """
    List all uploaded documents.
    Note: Pinecone doesn't have a native "list all" function, so we query with a dummy vector
    and use metadata to get unique documents.
    """
    if not index:
        raise HTTPException(status_code=500, detail="Pinecone not initialized")
    
    try:
        # Get all vectors by querying with a zero vector
        # This is a workaround since Pinecone doesn't have list_all
        dummy_vector = [0.0] * EMBEDDING_DIMENSION
        results = index.query(
            vector=dummy_vector,
            top_k=10000,
            include_metadata=True
        )
        
        # Extract unique documents
        documents = {}
        for match in results.matches:
            metadata = match.metadata
            title = metadata.get('title', 'Unknown')
            if title not in documents:
                documents[title] = {
                    'title': title,
                    'source': metadata.get('source', 'Unknown'),
                    'chunk_count': 0,
                    'tags': metadata.get('all_tags', [])
                }
            documents[title]['chunk_count'] += 1
        
        return {"documents": list(documents.values())}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list documents: {str(e)}")


@app.post("/upload")
async def upload_document(request: UploadRequest):
    """
    Upload a document to the knowledge base.
    Process: chunk → embed → tag → store
    """
    if not index:
        raise HTTPException(status_code=500, detail="Pinecone not initialized")
    
    try:
        # Step 1: Chunk the document
        chunks = chunk_text(request.text, CHUNK_SIZE, CHUNK_OVERLAP)
        
        if not chunks:
            raise HTTPException(status_code=400, detail="No chunks generated from text")
        
        # Step 2: Process each chunk
        vectors_to_upsert = []
        
        for i, chunk in enumerate(chunks):
            # Generate embedding
            embedding = generate_embedding(chunk)
            
            # Generate tags (keyword-based, comprehensive)
            tags = generate_tags(chunk)
            
            # Prepare metadata
            metadata = {
                'text': chunk,
                'title': request.title,
                'source': request.source,
                'chunk_index': i,
                'total_chunks': len(chunks),
                **tags  # Include all generated tags
            }
            
            # Add custom metadata if provided
            if request.metadata:
                metadata.update(request.metadata)
            
            # Prepare vector for upsert
            vector_id = f"{request.title}_{i}"
            vectors_to_upsert.append({
                'id': vector_id,
                'values': embedding,
                'metadata': metadata
            })
        
        # Step 3: Upsert to Pinecone (batch)
        index.upsert(vectors=vectors_to_upsert)
        
        return {
            "success": True,
            "title": request.title,
            "chunks_processed": len(chunks),
            "message": f"Successfully uploaded {len(chunks)} chunks"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@app.post("/query")
async def query_knowledge_base(request: QueryRequest):
    """
    Query the knowledge base using RAG.
    Process: embed question → search → augment → Claude → answer
    """
    if not index:
        raise HTTPException(status_code=500, detail="Pinecone not initialized")
    
    try:
        # Step 1: Generate embedding for question
        question_embedding = generate_embedding(request.question)
        
        # Step 2: Search Pinecone
        search_results = index.query(
            vector=question_embedding,
            top_k=request.top_k,
            filter=request.filters,
            include_metadata=True
        )
        
        if not search_results.matches:
            return {
                "answer": "I don't have enough information in my knowledge base to answer this question.",
                "sources": []
            }
        
        # Step 3: Prepare context from retrieved chunks
        context_parts = []
        sources = []
        
        for match in search_results.matches:
            metadata = match.metadata
            context_parts.append(f"[From: {metadata.get('title', 'Unknown')}]\n{metadata.get('text', '')}")
            
            sources.append({
                'title': metadata.get('title', 'Unknown'),
                'source': metadata.get('source', 'Unknown'),
                'score': float(match.score),
                'tags': metadata.get('all_tags', [])
            })
        
        context = "\n\n".join(context_parts)
        
        # Step 4: Query Claude with augmented prompt
        answer = query_claude(request.question, context)
        
        return {
            "answer": answer,
            "sources": sources,
            "chunks_retrieved": len(search_results.matches)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")


@app.delete("/documents/{title}")
async def delete_document(title: str):
    """
    Delete a document from the knowledge base.
    """
    if not index:
        raise HTTPException(status_code=500, detail="Pinecone not initialized")
    
    try:
        # Pinecone requires deletion by ID, so we need to find all chunk IDs for this title
        # Query to find all vectors with this title
        dummy_vector = [0.0] * EMBEDDING_DIMENSION
        results = index.query(
            vector=dummy_vector,
            top_k=10000,
            filter={"title": {"$eq": title}},
            include_metadata=True
        )
        
        if not results.matches:
            raise HTTPException(status_code=404, detail=f"Document '{title}' not found")
        
        # Delete all chunks
        ids_to_delete = [match.id for match in results.matches]
        index.delete(ids=ids_to_delete)
        
        return {
            "success": True,
            "title": title,
            "chunks_deleted": len(ids_to_delete)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")


# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
