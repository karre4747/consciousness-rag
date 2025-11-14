"""
Evolve Consciousness Engine - Backend API
FastAPI backend with Pinecone vector database, OpenAI embeddings, and Claude AI
"""

# Load environment variables FIRST before any other imports
from dotenv import load_dotenv
import os
load_dotenv(override=True)  # Override system environment variables

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from contextlib import asynccontextmanager
from typing import List, Optional, Dict, Any
import logging

# Import our modules
from pinecone import Pinecone, ServerlessSpec
from openai import OpenAI
from anthropic import Anthropic
import tiktoken
from tagging import generate_tags

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize clients
pinecone_client = None
openai_client = None
anthropic_client = None
index = None

# Configuration
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "evolve-consciousness")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-large")
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-5-20250929")
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))
PINECONE_DIMENSION = int(os.getenv("PINECONE_DIMENSION", "1536"))


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    global pinecone_client, openai_client, anthropic_client, index
    
    try:
        # Initialize Pinecone
        logger.info("Initializing Pinecone...")
        pinecone_client = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        
        # Create index if it doesn't exist
        existing_indexes = [idx.name for idx in pinecone_client.list_indexes()]
        
        if PINECONE_INDEX_NAME not in existing_indexes:
            logger.info(f"Creating Pinecone index: {PINECONE_INDEX_NAME}")
            pinecone_client.create_index(
                name=PINECONE_INDEX_NAME,
                dimension=PINECONE_DIMENSION,
                metric="cosine",
                spec=ServerlessSpec(
                    cloud="aws",
                    region="us-east-1"
                )
            )
        
        # Connect to index
        index = pinecone_client.Index(PINECONE_INDEX_NAME)
        logger.info(f"Connected to Pinecone index: {PINECONE_INDEX_NAME}")
        
        # Initialize OpenAI
        logger.info("Initializing OpenAI client...")
        openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Initialize Anthropic
        logger.info("Initializing Anthropic client...")
        anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        
        logger.info("All services initialized successfully!")
        
        yield
        
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        raise
    finally:
        logger.info("Shutting down...")


# Initialize FastAPI app
app = FastAPI(
    title="Evolve Consciousness Engine",
    description="Quantum-aware RAG system for consciousness, recovery, and spiritual transformation",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# === PYDANTIC MODELS ===

class UploadRequest(BaseModel):
    """Request model for document upload"""
    text: str
    title: str
    source: Optional[str] = None
    program_level: Optional[str] = "beginner"
    use_ai_tagging: Optional[bool] = False


class QueryRequest(BaseModel):
    """Request model for RAG query"""
    question: str
    program_level: Optional[str] = None
    filters: Optional[Dict[str, Any]] = None
    top_k: Optional[int] = 5


class QueryResponse(BaseModel):
    """Response model for RAG query"""
    answer: str
    sources: List[Dict[str, Any]]
    metadata: Dict[str, Any]


# === HELPER FUNCTIONS ===

def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    """Split text into overlapping chunks"""
    encoding = tiktoken.encoding_for_model("gpt-4")
    tokens = encoding.encode(text)
    
    chunks = []
    start = 0
    
    while start < len(tokens):
        end = start + chunk_size
        chunk_tokens = tokens[start:end]
        chunk_text = encoding.decode(chunk_tokens)
        chunks.append(chunk_text)
        start += chunk_size - overlap
    
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
        logger.error(f"Embedding generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Embedding generation failed: {str(e)}")


def generate_answer(question: str, context_chunks: List[Dict[str, Any]], program_level: str = "beginner") -> str:
    """Generate answer using Claude with retrieved context"""
    
    # Build context from retrieved chunks
    context = "\n\n".join([
        f"[Source: {chunk['metadata'].get('title', 'Unknown')}]\n{chunk['metadata'].get('text', '')}"
        for chunk in context_chunks
    ])
    
    # Persona based on program level
    personas = {
        "beginner": "You are a compassionate guide introducing consciousness and recovery concepts. Use simple language, relatable examples, and emphasize hope and practical steps.",
        "intermediate": "You are a knowledgeable teacher bridging science and spirituality. Integrate neuroscience, quantum concepts, and mystical traditions with clarity and depth.",
        "advanced": "You are a master philosopher and mystic. Synthesize esoteric wisdom, quantum physics, and consciousness studies. Speak to the initiated with precision and profound insight."
    }
    
    persona = personas.get(program_level, personas["beginner"])
    
    prompt = f"""{persona}

Based on the following knowledge from the Evolve Consciousness database, answer the user's question with wisdom, clarity, and practical guidance.

CONTEXT:
{context}

QUESTION:
{question}

Provide a comprehensive answer that:
1. Directly addresses the question
2. Integrates relevant concepts from the context
3. Offers practical application or next steps
4. Maintains the appropriate depth for the {program_level} level

ANSWER:"""

    try:
        message = anthropic_client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return message.content[0].text
        
    except Exception as e:
        logger.error(f"Answer generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Answer generation failed: {str(e)}")


# === API ENDPOINTS ===

@app.get("/")
def read_root():
    """Health check endpoint"""
    return {
        "status": "Evolve Consciousness Engine Online",
        "version": "1.0.0",
        "services": {
            "pinecone": index is not None,
            "openai": openai_client is not None,
            "anthropic": anthropic_client is not None
        }
    }


@app.get("/health")
def health_check():
    """Detailed health check"""
    try:
        # Check Pinecone
        stats = index.describe_index_stats()
        
        return {
            "status": "healthy",
            "pinecone": {
                "connected": True,
                "index": PINECONE_INDEX_NAME,
                "total_vectors": stats.total_vector_count,
                "dimension": PINECONE_DIMENSION
            },
            "openai": {"connected": openai_client is not None},
            "anthropic": {"connected": anthropic_client is not None}
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }


@app.post("/upload")
async def upload_document(request: UploadRequest):
    """
    Upload and process a document for ingestion into the vector database
    
    This endpoint:
    1. Chunks the document
    2. Generates embeddings for each chunk
    3. Generates metadata tags
    4. Stores in Pinecone
    """
    try:
        logger.info(f"Processing document: {request.title}")
        
        # Chunk the text
        chunks = chunk_text(request.text)
        logger.info(f"Created {len(chunks)} chunks")
        
        # Process each chunk
        vectors_to_upsert = []
        
        for i, chunk in enumerate(chunks):
            # Generate embedding
            embedding = generate_embedding(chunk)
            
            # Generate tags
            tags = generate_tags(chunk, use_ai=request.use_ai_tagging)
            
            # Create metadata
            metadata = {
                "text": chunk,
                "title": request.title,
                "source": request.source or "unknown",
                "program_level": request.program_level,
                "chunk_index": i,
                "total_chunks": len(chunks),
                "tags": tags.get("tags", []),
                "detected_categories": tags.get("detected_categories", {}),
                "primary_theme": tags.get("primary_theme", ""),
                "consciousness_level": tags.get("consciousness_level", "")
            }
            
            # Create vector ID
            vector_id = f"{request.title.replace(' ', '_')}_{i}"
            
            vectors_to_upsert.append({
                "id": vector_id,
                "values": embedding,
                "metadata": metadata
            })
        
        # Upsert to Pinecone
        index.upsert(vectors=vectors_to_upsert)
        
        logger.info(f"Successfully uploaded {len(vectors_to_upsert)} vectors")
        
        return {
            "status": "success",
            "message": f"Document '{request.title}' processed successfully",
            "chunks_created": len(chunks),
            "vectors_uploaded": len(vectors_to_upsert)
        }
        
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/query", response_model=QueryResponse)
async def query_knowledge(request: QueryRequest):
    """
    Query the knowledge base using RAG
    
    This endpoint:
    1. Generates embedding for the question
    2. Searches Pinecone for relevant chunks
    3. Uses Claude to generate a contextual answer
    """
    try:
        logger.info(f"Processing query: {request.question}")
        
        # Generate embedding for question
        question_embedding = generate_embedding(request.question)
        
        # Build filter
        filter_dict = request.filters or {}
        if request.program_level:
            filter_dict["program_level"] = request.program_level
        
        # Query Pinecone
        query_response = index.query(
            vector=question_embedding,
            top_k=request.top_k,
            include_metadata=True,
            filter=filter_dict if filter_dict else None
        )
        
        # Extract matches
        matches = query_response.matches
        
        if not matches:
            return QueryResponse(
                answer="I couldn't find relevant information in the knowledge base to answer your question. Please try rephrasing or asking about a different topic.",
                sources=[],
                metadata={"matches_found": 0}
            )
        
        # Generate answer using Claude
        answer = generate_answer(
            request.question,
            matches,
            request.program_level or "beginner"
        )
        
        # Format sources
        sources = [
            {
                "title": match.metadata.get("title", "Unknown"),
                "source": match.metadata.get("source", "Unknown"),
                "score": match.score,
                "tags": match.metadata.get("tags", [])
            }
            for match in matches
        ]
        
        return QueryResponse(
            answer=answer,
            sources=sources,
            metadata={
                "matches_found": len(matches),
                "program_level": request.program_level or "beginner",
                "model": CLAUDE_MODEL
            }
        )
        
    except Exception as e:
        logger.error(f"Query failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats")
def get_stats():
    """Get database statistics"""
    try:
        stats = index.describe_index_stats()
        
        return {
            "index_name": PINECONE_INDEX_NAME,
            "total_vectors": stats.total_vector_count,
            "dimension": PINECONE_DIMENSION,
            "namespaces": stats.namespaces
        }
    except Exception as e:
        logger.error(f"Stats retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
