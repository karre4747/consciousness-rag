#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Evolve Consciousness Engine - Backend API
FastAPI backend with Pinecone vector database, OpenAI embeddings, and Claude AI
"""

# Load environment variables FIRST before any other imports
from dotenv import load_dotenv
import os
import sys

# Ensure UTF-8 encoding
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8')

load_dotenv(override=True)  # Override system environment variables

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
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
from spending_tracker import SpendingTracker
from cost_estimator import estimate_claude_cost

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize clients
pinecone_client = None
openai_client = None
anthropic_client = None
index = None
spending_tracker = SpendingTracker()  # Initialize spending tracker

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

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")


# === PYDANTIC MODELS ===

class UploadRequest(BaseModel):
    """Request model for document upload"""
    text: str
    title: str
    source: Optional[str] = None
    use_ai_tagging: Optional[bool] = False  # Default to False (keyword-based, FREE)
    ai_provider: Optional[str] = "ollama"  # "ollama" (FREE) or "openai" (paid)
    ollama_model: Optional[str] = "llama3.1"  # Ollama model to use


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
    """Serve upload interface"""
    return FileResponse("static/index.html")


@app.get("/api")
def api_status():
    """API status endpoint"""
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


def clean_text_for_metadata(text: str) -> str:
    """
    Clean text to ensure it can be safely encoded in UTF-8 for Pinecone metadata
    Removes problematic characters that cause encoding issues
    """
    import re
    # Remove replacement characters and other problematic Unicode
    text = text.replace('\uFFFD', '')  # Replacement character
    text = text.replace('\x00', '')  # Null character
    # Remove control characters except newline, tab, carriage return
    text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
    # Ensure it's valid UTF-8
    text = text.encode('utf-8', errors='ignore').decode('utf-8')
    return text


@app.post("/upload")
async def upload_document(request: UploadRequest):
    """
    Upload and process a document for ingestion into the vector database

    This endpoint:
    1. Chunks the document
    2. Generates embeddings for each chunk
    3. Generates metadata tags
    4. Stores in Pinecone in batches (to handle large documents)
    """
    try:
        logger.info(f"Processing document: {request.title}")

        # Chunk the text
        chunks = chunk_text(request.text)
        total_chunks = len(chunks)
        logger.info(f"Created {total_chunks} chunks")

        # Process in batches to handle large documents
        BATCH_SIZE = 50  # Process 50 chunks at a time
        total_uploaded = 0

        for batch_start in range(0, total_chunks, BATCH_SIZE):
            batch_end = min(batch_start + BATCH_SIZE, total_chunks)
            batch_chunks = chunks[batch_start:batch_end]

            logger.info(f"Processing batch {batch_start}-{batch_end} of {total_chunks}")

            vectors_to_upsert = []

            for i, chunk in enumerate(batch_chunks):
                chunk_index = batch_start + i

                try:
                    # Clean chunk text to ensure UTF-8 compatibility
                    clean_chunk = clean_text_for_metadata(chunk)

                    # Generate embedding
                    embedding = generate_embedding(clean_chunk)

                    # Generate tags (pass title for program_level detection and AI provider)
                    tags = generate_tags(
                        clean_chunk,
                        use_ai=request.use_ai_tagging,
                        ai_provider=request.ai_provider,
                        title=request.title,
                        ollama_model=request.ollama_model
                    )

                    # Create metadata with all enhanced tags
                    metadata = {
                        "text": clean_chunk,
                        "title": clean_text_for_metadata(request.title),
                        "source": request.source or "unknown",
                        "chunk_index": chunk_index,
                        "total_chunks": total_chunks,
                        "tags": tags.get("tags", []),
                        "detected_categories": tags.get("detected_categories", {}),
                        "primary_theme": tags.get("primary_theme", ""),
                        "consciousness_level": tags.get("consciousness_level", ""),
                        "emotions": tags.get("emotions", []),
                        "primary_chakra": tags.get("primary_chakra"),
                        "tradition": tags.get("tradition"),
                        "teacher": tags.get("teacher"),
                        "ascension_path": tags.get("ascension_path"),
                        "bridge_concept": tags.get("bridge_concept"),
                        "recovery_focus": tags.get("recovery_focus"),
                        "healing_modality": tags.get("healing_modality")
                    }

                    # Add program_level only if detected (addiction-specific content)
                    if "program_level" in tags:
                        metadata["program_level"] = tags["program_level"]

                    # Create vector ID
                    vector_id = f"{request.title.replace(' ', '_')}_{chunk_index}"

                    vectors_to_upsert.append({
                        "id": vector_id,
                        "values": embedding,
                        "metadata": metadata
                    })

                except Exception as chunk_error:
                    logger.error(f"Error processing chunk {chunk_index}: {chunk_error}")
                    # Continue processing other chunks even if one fails
                    continue

            # Upsert batch to Pinecone
            if vectors_to_upsert:
                try:
                    index.upsert(vectors=vectors_to_upsert)
                    total_uploaded += len(vectors_to_upsert)
                    logger.info(f"Uploaded batch: {len(vectors_to_upsert)} vectors (total: {total_uploaded}/{total_chunks})")
                except Exception as upsert_error:
                    logger.error(f"Error upserting batch: {upsert_error}")
                    raise HTTPException(status_code=500, detail=f"Failed to upload batch: {str(upsert_error)}")

        logger.info(f"Successfully uploaded {total_uploaded} vectors")

        return {
            "status": "success",
            "message": f"Document '{request.title}' processed successfully",
            "chunks_created": total_chunks,
            "vectors_uploaded": total_uploaded
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


# === DOCUMENT MANAGEMENT ENDPOINTS ===

@app.get("/uploaded-documents")
async def get_uploaded_documents():
    """
    Get list of all unique documents currently in Pinecone

    Returns:
        List of documents with titles, chunk counts
    """
    try:
        # Query Pinecone to get all vectors
        query_vector = [0.0] * PINECONE_DIMENSION
        results = index.query(
            vector=query_vector,
            top_k=10000,  # Maximum allowed by Pinecone
            include_metadata=True
        )

        # Group by title to get unique documents
        documents_dict = {}
        for match in results.matches:
            title = match.metadata.get('title', 'Unknown')

            if title not in documents_dict:
                documents_dict[title] = {
                    'title': title,
                    'source': match.metadata.get('source', ''),
                    'chunk_count': 0,
                    'total_chunks': match.metadata.get('total_chunks', 0)
                }

            documents_dict[title]['chunk_count'] += 1

        # Convert to list and sort alphabetically
        doc_list = sorted(documents_dict.values(), key=lambda x: x['title'].lower())

        return {
            "status": "success",
            "total_documents": len(doc_list),
            "documents": doc_list
        }

    except Exception as e:
        logger.error(f"Failed to get uploaded documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/check-duplicate")
async def check_duplicate(request: Dict[str, str]):
    """
    Check if a document with this title already exists

    Args:
        request: {"title": "document_name"}

    Returns:
        {"exists": bool, "chunk_count": int}
    """
    try:
        title = request.get("title")

        # Query Pinecone with metadata filter to find this title
        query_vector = [0.0] * PINECONE_DIMENSION
        results = index.query(
            vector=query_vector,
            top_k=100,  # Get enough to count chunks
            include_metadata=True,
            filter={"title": title}
        )

        exists = len(results.matches) > 0
        chunk_count = len(results.matches) if exists else 0

        return {
            "status": "success",
            "exists": exists,
            "chunk_count": chunk_count,
            "title": title
        }

    except Exception as e:
        logger.error(f"Duplicate check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/delete-document/{title}")
async def delete_document(title: str):
    """
    Delete all chunks of a document from Pinecone

    Args:
        title: Document title (URL-encoded)

    Returns:
        Confirmation with number of chunks deleted
    """
    try:
        # First, query to find all chunks with this title
        query_vector = [0.0] * PINECONE_DIMENSION
        results = index.query(
            vector=query_vector,
            top_k=10000,  # Get all chunks
            include_metadata=True,
            filter={"title": title}
        )

        # Collect all IDs to delete
        ids_to_delete = [match.id for match in results.matches]

        if not ids_to_delete:
            return {
                "status": "success",
                "message": f"No chunks found for '{title}'",
                "chunks_deleted": 0
            }

        # Delete all chunks
        index.delete(ids=ids_to_delete)

        logger.info(f"Deleted {len(ids_to_delete)} chunks of document '{title}'")

        return {
            "status": "success",
            "message": f"Deleted {len(ids_to_delete)} chunks of '{title}'",
            "chunks_deleted": len(ids_to_delete)
        }

    except Exception as e:
        logger.error(f"Delete failed for '{title}': {e}")
        raise HTTPException(status_code=500, detail=str(e))


# === CLAUDE SPENDING TRACKING ENDPOINTS ===

@app.get("/spending-dashboard")
async def get_spending_dashboard(month: Optional[str] = None):
    """
    Get spending stats and history for current/specified month

    Args:
        month: Optional month in format "2025-11"

    Returns:
        Monthly stats and detailed history
    """
    try:
        stats = spending_tracker.get_monthly_stats(month)
        history = spending_tracker.get_monthly_history(month)

        # Calculate estimated pages from tokens
        total_pages = round(stats['total_input_tokens'] / 650) if stats['total_input_tokens'] else 0

        return {
            "status": "success",
            "stats": {
                **stats,
                "estimated_pages_analyzed": total_pages,
                "remaining_budget": round(stats['monthly_cap'] - stats['total_cost'], 2),
                "budget_used_percentage": round(
                    (stats['total_cost'] / stats['monthly_cap']) * 100, 1
                ) if stats['monthly_cap'] > 0 else 0
            },
            "history": history
        }

    except Exception as e:
        logger.error(f"Spending dashboard failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/update-spending-cap")
async def update_spending_cap(request: Dict[str, float]):
    """
    Update monthly spending cap

    Args:
        request: {"new_cap": 40.00}
    """
    try:
        new_cap = request.get("new_cap")

        if new_cap is None or new_cap < 0:
            raise HTTPException(status_code=400, detail="Cap must be a positive number")

        spending_tracker.set_monthly_cap(new_cap)

        return {
            "status": "success",
            "message": f"Monthly cap updated to ${new_cap}",
            "new_cap": new_cap
        }

    except Exception as e:
        logger.error(f"Update spending cap failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/estimate-analysis-cost")
async def estimate_analysis_cost(request: Dict[str, Any]):
    """
    Calculate accurate cost BEFORE running Claude analysis

    Args:
        request: {
            "analysis_type": "recent" | "full" | "theme",
            "limit": 50 (for "recent"),
            "filters": {...} (for "theme")
        }

    Returns:
        Detailed cost estimate with budget check
    """
    try:
        analysis_type = request.get("analysis_type", "recent")
        limit = request.get("limit", 50)
        filters = request.get("filters")

        # Query Pinecone based on analysis type
        # For now, we'll do a simple query - you can expand this later
        # This is a placeholder that gets recent vectors
        query_vector = [0.0] * PINECONE_DIMENSION

        if analysis_type == "recent":
            results = index.query(
                vector=query_vector,
                top_k=min(limit, 10000),
                include_metadata=True
            )
        elif analysis_type == "full":
            results = index.query(
                vector=query_vector,
                top_k=10000,  # Max we can get in one query
                include_metadata=True
            )
        elif analysis_type == "theme":
            results = index.query(
                vector=query_vector,
                top_k=10000,
                include_metadata=True,
                filter=filters or {}
            )
        else:
            raise HTTPException(status_code=400, detail="Invalid analysis_type")

        # Calculate cost using actual token counts
        documents = [{"metadata": match.metadata} for match in results.matches]

        if not documents:
            return {
                "status": "success",
                "estimate": {
                    "total_documents": 0,
                    "total_cost": 0,
                    "message": "No documents found to analyze"
                },
                "budget": spending_tracker.can_afford(0)
            }

        estimate = estimate_claude_cost(documents, batch_size=15)

        # Check budget
        budget_check = spending_tracker.can_afford(estimate['total_cost'])

        return {
            "status": "success",
            "estimate": estimate,
            "budget": budget_check,
            "analysis_type": analysis_type
        }

    except Exception as e:
        logger.error(f"Cost estimation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
