"""
Evolve Consciousness Engine - Complete Backend
Full-featured RAG system with Claude analysis and training data generation
Updated: December 22, 2025
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
import uuid
from pinecone import Pinecone, ServerlessSpec
from openai import OpenAI
from anthropic import Anthropic

# Import our modules
import database_complete as database
from tagging_complete import (
    generate_tags, 
    analyze_document_with_claude,
    analyze_document_group_with_claude
)

# ============================================================================
# CONFIGURATION
# ============================================================================

app = FastAPI(title="Evolve Consciousness Engine")

# Environment variables
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "consciousness-rag")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Constants
EMBEDDING_MODEL = "text-embedding-3-large"
EMBEDDING_DIMENSION = 3072
CHUNK_SIZE = 1800  # Characters per chunk (your optimal size)
CLAUDE_MAX_CHARS = 10000  # Max chars to send to Claude per document

# Initialize clients
openai_client = OpenAI(api_key=OPENAI_API_KEY)
anthropic_client = Anthropic(api_key=ANTHROPIC_API_KEY)

# Initialize Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)
index = None

# Initialize database
database.init_db()


# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class UploadRequest(BaseModel):
    title: str
    content: str
    source: str = "Unknown"
    metadata: Optional[Dict[str, Any]] = None


class QueryRequest(BaseModel):
    question: str
    top_k: int = 5
    filters: Optional[Dict[str, Any]] = None


class AnalyzeRequest(BaseModel):
    level: str = "individual"  # "individual" or "grouped"
    filter_topics: Optional[List[str]] = None


# ============================================================================
# INITIALIZATION
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize Pinecone index on startup"""
    global index
    
    try:
        # Check if index exists
        existing_indexes = [idx.name for idx in pc.list_indexes()]
        
        if PINECONE_INDEX_NAME not in existing_indexes:
            # Create index
            pc.create_index(
                name=PINECONE_INDEX_NAME,
                dimension=EMBEDDING_DIMENSION,
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1")
            )
            print(f"Created Pinecone index: {PINECONE_INDEX_NAME}")
        
        # Connect to index
        index = pc.Index(PINECONE_INDEX_NAME)
        print(f"Connected to Pinecone index: {PINECONE_INDEX_NAME}")
        
    except Exception as e:
        print(f"Error initializing Pinecone: {e}")


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def chunk_text(text: str, chunk_size: int = CHUNK_SIZE) -> List[str]:
    """
    Chunk text into smaller pieces by sentences
    Maintains sentence boundaries for better semantic coherence
    """
    # Split by sentences (simple approach)
    sentences = text.replace('!', '.').replace('?', '.').split('.')
    sentences = [s.strip() + '.' for s in sentences if s.strip()]
    
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        if len(current_chunk) + len(sentence) <= chunk_size:
            current_chunk += " " + sentence
        else:
            if current_chunk.strip():
                chunks.append(current_chunk.strip())
            current_chunk = sentence
    
    # Add final chunk
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
    
    return chunks


def generate_embedding(text: str) -> List[float]:
    """Generate embedding using OpenAI"""
    try:
        response = openai_client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Embedding generation failed: {str(e)}")


def query_claude(prompt: str, context: str) -> str:
    """Query Claude for RAG response"""
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
# CORE ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "Evolve Consciousness Engine",
        "version": "2.0-complete"
    }


@app.get("/health")
async def health():
    """Detailed health check"""
    return {
        "pinecone": "connected" if index else "disconnected",
        "openai": "configured" if OPENAI_API_KEY else "not configured",
        "anthropic": "configured" if ANTHROPIC_API_KEY else "not configured",
        "database": "initialized",
        "chunk_size": CHUNK_SIZE
    }


@app.get("/stats")
async def get_stats():
    """Get system statistics"""
    try:
        # Get Pinecone stats
        index_stats = index.describe_index_stats() if index else {}
        
        # Get database stats
        db_stats = database.get_stats()
        
        return {
            "pinecone": {
                "total_vectors": index_stats.get('total_vector_count', 0),
                "dimension": index_stats.get('dimension', 0)
            },
            "database": db_stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stats retrieval failed: {str(e)}")


@app.post("/upload")
async def upload_document(request: UploadRequest):
    """
    Upload a document to the knowledge base
    Process: chunk (1800 chars) → embed → tag (keyword) → store
    """
    if not index:
        raise HTTPException(status_code=500, detail="Pinecone not initialized")
    
    try:
        # Step 1: Chunk the document
        chunks = chunk_text(request.content, CHUNK_SIZE)
        
        if not chunks:
            raise HTTPException(status_code=400, detail="Document produced no chunks")
        
        # Step 2: Process each chunk
        vectors_to_upsert = []
        
        for i, chunk in enumerate(chunks):
            # Generate embedding
            embedding = generate_embedding(chunk)
            
            # Generate tags (keyword-based, fast)
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
        
        # Step 4: Track in database
        database.add_document(request.title, request.source, len(chunks))
        
        return {
            "success": True,
            "title": request.title,
            "chunks_processed": len(chunks),
            "chunk_size": CHUNK_SIZE,
            "message": f"Successfully uploaded {len(chunks)} chunks"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@app.post("/query")
async def query_knowledge_base(request: QueryRequest):
    """
    Query the knowledge base using RAG
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


@app.get("/documents")
async def list_documents():
    """List all documents in the database"""
    try:
        documents = database.get_all_documents()
        return {"documents": documents}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list documents: {str(e)}")


@app.delete("/documents/{title}")
async def delete_document(title: str):
    """Delete a document from the knowledge base"""
    if not index:
        raise HTTPException(status_code=500, detail="Pinecone not initialized")
    
    try:
        # Delete from Pinecone (delete all chunks)
        # Note: Pinecone requires deletion by ID
        # We'll use a prefix match to delete all chunks for this title
        index.delete(filter={"title": {"$eq": title}})
        
        # Delete from database
        database.delete_document(title)
        
        return {
            "success": True,
            "message": f"Deleted document: {title}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")


# ============================================================================
# ANALYSIS ENDPOINTS (CLAUDE DEEP ANALYSIS)
# ============================================================================

@app.post("/analyze/start")
async def start_analysis(request: AnalyzeRequest):
    """
    Start Claude analysis of documents
    This is MANUAL TRIGGER to prevent overload
    
    Level 1 (individual): Analyze each document separately
    Level 2 (grouped): Find connections across related documents
    """
    if not index:
        raise HTTPException(status_code=500, detail="Pinecone not initialized")
    
    try:
        # Get unanalyzed documents
        documents = database.get_unanalyzed_documents()
        
        if not documents:
            return {
                "message": "No documents need analysis",
                "total_documents": 0
            }
        
        # Create analysis job
        job_id = str(uuid.uuid4())
        level = 1 if request.level == "individual" else 2
        database.create_analysis_job(job_id, level, len(documents))
        
        # Start analysis (this will run in background in production)
        # For now, we'll process synchronously with rate limiting
        
        if request.level == "individual":
            # Level 1: Individual document analysis
            for i, doc in enumerate(documents):
                # Get document text from Pinecone
                # Query for all chunks of this document
                results = index.query(
                    vector=[0] * EMBEDDING_DIMENSION,  # Dummy vector
                    top_k=doc['chunk_count'],
                    filter={"title": {"$eq": doc['title']}},
                    include_metadata=True
                )
                
                # Combine chunks
                full_text = " ".join([
                    match.metadata.get('text', '') 
                    for match in results.matches
                ])
                
                # Analyze with Claude (rate-limited)
                analysis = analyze_document_with_claude(
                    full_text, 
                    doc['title'], 
                    max_chars=CLAUDE_MAX_CHARS
                )
                
                # Save analysis
                if 'error' not in analysis:
                    database.save_document_analysis(doc['id'], analysis)
                
                # Update progress
                database.update_analysis_job_progress(
                    job_id, 
                    i + 1, 
                    doc['title']
                )
        
        # Complete job
        database.complete_analysis_job(job_id)
        
        return {
            "job_id": job_id,
            "status": "completed",
            "total_documents": len(documents),
            "level": request.level
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.get("/analyze/status/{job_id}")
async def get_analysis_status(job_id: str):
    """Get status of an analysis job"""
    try:
        job = database.get_analysis_job(job_id)
        
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        return job
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")


@app.get("/analyze/results")
async def get_analysis_results():
    """Get analysis results summary"""
    try:
        stats = database.get_stats()
        connections = database.get_all_connections()
        
        return {
            "analyzed_documents": stats['analyzed_documents'],
            "total_connections": stats['total_connections'],
            "top_connections": connections[:10]  # Top 10 strongest connections
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Results retrieval failed: {str(e)}")


@app.get("/document/{title}/analysis")
async def get_document_analysis(title: str):
    """Get Claude's analysis for a specific document"""
    try:
        doc = database.get_document_by_title(title)
        
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        
        analysis = database.get_document_analysis(doc['id'])
        
        if not analysis:
            return {
                "message": "Document not yet analyzed",
                "status": doc['analysis_status']
            }
        
        return {
            "title": title,
            "analysis": analysis,
            "analyzed_at": analysis['analyzed_at']
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis retrieval failed: {str(e)}")


# ============================================================================
# TRAINING DATA ENDPOINTS
# ============================================================================

@app.post("/training/generate")
async def generate_training_data():
    """
    Generate training data from connections
    Creates prompt/completion pairs for fine-tuning
    """
    try:
        connections = database.get_all_connections()
        
        if not connections:
            return {
                "message": "No connections found. Run analysis first.",
                "training_pairs": 0
            }
        
        # Generate training pairs from connections
        pairs_created = 0
        
        for conn in connections:
            # Create prompt/completion pair
            prompt = f"How does {conn['doc1_title']} relate to {conn['doc2_title']}?"
            completion = conn['description']
            
            # Save to database
            database.save_training_pair(
                prompt=prompt,
                completion=completion,
                source_doc1=conn['doc1_title'],
                source_doc2=conn['doc2_title'],
                quality_score=conn['strength']
            )
            pairs_created += 1
        
        return {
            "success": True,
            "training_pairs_created": pairs_created,
            "message": "Training data generated successfully"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Training data generation failed: {str(e)}")


@app.get("/training/export")
async def export_training_data():
    """
    Export training data in .jsonl format for fine-tuning
    """
    try:
        training_pairs = database.get_training_data(exported_only=False)
        
        if not training_pairs:
            return {
                "message": "No training data available",
                "pairs": 0
            }
        
        # Format for OpenAI fine-tuning
        jsonl_data = []
        for pair in training_pairs:
            jsonl_data.append({
                "messages": [
                    {
                        "role": "system",
                        "content": "You are the Evolve Consciousness Engine, an expert in consciousness, mysticism, and spiritual transformation."
                    },
                    {
                        "role": "user",
                        "content": pair['prompt']
                    },
                    {
                        "role": "assistant",
                        "content": pair['completion']
                    }
                ]
            })
        
        return {
            "training_data": jsonl_data,
            "total_pairs": len(jsonl_data),
            "format": "openai_jsonl"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


# ============================================================================
# SERVE FRONTEND
# ============================================================================

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/app")
async def serve_app():
    """Serve the frontend application"""
    return FileResponse("static/index_complete.html")


# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
