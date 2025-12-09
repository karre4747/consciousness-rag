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

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from contextlib import asynccontextmanager
from typing import List, Optional, Dict, Any
import asyncio
import logging

# Import our modules
from pinecone import Pinecone, ServerlessSpec
from openai import OpenAI
from anthropic import Anthropic
import tiktoken
from tagging import generate_tags, claude_second_pass_analysis
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


class RetagRequest(BaseModel):
    """Request model for re-tagging existing documents"""
    document_titles: Optional[List[str]] = None  # None or empty = all documents
    ai_provider: Optional[str] = "ollama"  # "ollama" (FREE) or "openai" (paid)
    ollama_model: Optional[str] = "llama3.1"  # Ollama model to use
    batch_size: Optional[int] = 50  # Process chunks in batches


class AnalyzeRequest(BaseModel):
    """Request model for Claude deep analysis"""
    analysis_type: Optional[str] = "recent"  # "recent", "full", "selected"
    limit: Optional[int] = 50
    filters: Optional[Dict[str, Any]] = None
    selected_titles: Optional[List[str]] = None


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
    
    # Build context from retrieved chunks (with safety checks for Pinecone match objects)
    context_parts = []
    for chunk in context_chunks:
        # Handle Pinecone match objects (they have .metadata attribute, not dict key)
        if hasattr(chunk, 'metadata'):
            metadata = chunk.metadata
        elif isinstance(chunk, dict):
            metadata = chunk.get('metadata', {})
        else:
            continue  # Skip invalid chunks
        
        # Safely extract title and text
        title = metadata.get('title', 'Unknown') if hasattr(metadata, 'get') else getattr(metadata, 'title', 'Unknown')
        text = metadata.get('text', '') if hasattr(metadata, 'get') else getattr(metadata, 'text', '')
        
        if text:  # Only add non-empty chunks
            context_parts.append(f"[Source: {title}]\n{text}")
    
    context = "\n\n".join(context_parts) if context_parts else "No context available."
    
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
    return FileResponse(
        "static/index.html",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
            "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self' http://localhost:* https://*;"
        }
    )


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
    Clean text to ensure it can be safely encoded for Pinecone metadata
    Converts all text to ASCII-safe characters to avoid encoding issues
    """
    import re
    import unicodedata

    # Normalize Unicode to decomposed form, then recompose
    text = unicodedata.normalize('NFKC', text)

    # Remove replacement characters and null characters
    text = text.replace('\uFFFD', '')  # Replacement character
    text = text.replace('\x00', '')  # Null character

    # Remove control characters except newline, tab, carriage return
    text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F-\x9F]', '', text)

    # Remove zero-width characters and other invisible characters
    text = re.sub(r'[\u200B-\u200D\uFEFF]', '', text)

    # Replace smart quotes and special characters with ASCII equivalents
    replacements = {
        '\u2018': "'",  # Left single quote
        '\u2019': "'",  # Right single quote
        '\u201C': '"',  # Left double quote
        '\u201D': '"',  # Right double quote
        '\u2013': '-',  # En dash
        '\u2014': '-',  # Em dash
        '\u2026': '...',  # Ellipsis
    }
    for old, new in replacements.items():
        text = text.replace(old, new)

    # Convert to ASCII, replacing non-ASCII characters
    text = text.encode('ascii', errors='ignore').decode('ascii')

    return text


def clean_metadata_for_pinecone(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """
    Clean metadata dictionary to ensure all values are Pinecone-compatible
    Converts None to empty strings, ensures lists are lists, etc.
    """
    cleaned = {}

    for key, value in metadata.items():
        if value is None:
            # Convert None to empty string or empty list based on key
            if key.startswith('all_') or key in ['tags', 'emotions']:
                cleaned[key] = []
            else:
                cleaned[key] = ""
        elif isinstance(value, list):
            # Ensure lists contain only strings
            cleaned[key] = [str(item) if item is not None else "" for item in value]
        elif isinstance(value, (str, int, float, bool)):
            # Keep strings, numbers, booleans as-is
            cleaned[key] = value
        else:
            # Convert anything else to string
            cleaned[key] = str(value)

    return cleaned


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

        # Validate input
        if not request.text or not request.text.strip():
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        if not request.title or not request.title.strip():
            raise HTTPException(status_code=400, detail="Title cannot be empty")

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
                    # Extract detected_categories for flattening
                    detected_cats = tags.get("detected_categories", {})

                    metadata = {
                        "text": clean_chunk,
                        "title": clean_text_for_metadata(request.title),
                        "source": request.source or "unknown",
                        "chunk_index": chunk_index,
                        "total_chunks": total_chunks,

                        # Core tags
                        "tags": tags.get("tags", []),
                        "primary_theme": tags.get("primary_theme", ""),
                        "consciousness_level": tags.get("consciousness_level", ""),
                        "emotions": tags.get("emotions", []),

                        # Primary/individual fields (for simple queries)
                        "primary_chakra": tags.get("primary_chakra", ""),
                        "tradition": tags.get("tradition", ""),
                        "teacher": tags.get("teacher", ""),
                        "ascension_path": tags.get("ascension_path", ""),
                        "bridge_concept": tags.get("bridge_concept", ""),
                        "recovery_focus": tags.get("recovery_focus", ""),
                        "healing_modality": tags.get("healing_modality", ""),

                        # ALL detected categories as lists (for comprehensive queries & membership filtering)
                        "all_chakras": detected_cats.get("chakras", []),
                        "all_meridians": detected_cats.get("meridians", []),
                        "all_12_steps": detected_cats.get("12_steps", []),
                        "all_consciousness_levels": detected_cats.get("consciousness_level", []),
                        "all_traditions": detected_cats.get("traditions", []),
                        "all_teachers": detected_cats.get("teachers", []),
                        "all_quantum_physics": detected_cats.get("quantum_physics", []),
                        "all_quantum_particles": detected_cats.get("quantum_particles", []),
                        "all_ascension_paths": detected_cats.get("ascension_paths", []),
                        "all_bridge_concepts": detected_cats.get("bridge_concepts", []),
                        "all_universal_laws": detected_cats.get("universal_laws", []),
                        "all_healing_modalities": detected_cats.get("healing_modalities", []),
                        "all_sacred_geometry": detected_cats.get("sacred_geometry", []),
                        "all_subtle_bodies": detected_cats.get("subtle_bodies", []),
                        "all_addiction_types": detected_cats.get("addiction_type", [])
                    }

                    # Add program_level only if detected (addiction-specific content)
                    if "program_level" in tags:
                        metadata["program_level"] = tags["program_level"]

                    # Clean metadata for Pinecone compatibility (convert None to empty strings)
                    metadata = clean_metadata_for_pinecone(metadata)

                    # Create vector ID (sanitize title to avoid special characters)
                    import re
                    safe_title = re.sub(r'[^a-zA-Z0-9_-]', '_', request.title)
                    vector_id = f"{safe_title}_{chunk_index}"

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

        # Validate and clamp top_k to prevent slow queries
        requested_top_k = request.top_k or 5
        top_k = max(1, min(20, requested_top_k))
        
        # Generate embedding for question
        question_embedding = generate_embedding(request.question)
        
        # Build filter
        filter_dict = request.filters or {}
        if request.program_level:
            filter_dict["program_level"] = request.program_level
        
        # Query Pinecone
        query_response = index.query(
            vector=question_embedding,
            top_k=top_k,
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
        
        # Generate answer using Claude with timeout to avoid long-running requests
        try:
            answer = await asyncio.wait_for(
                asyncio.to_thread(
                    generate_answer,
                    request.question,
                    matches,
                    request.program_level or "beginner"
                ),
                timeout=30
            )
        except asyncio.TimeoutError:
            raise HTTPException(status_code=504, detail="Answer generation timed out. Please try again.")
        
        # Format sources with full text and metadata for UI display
        sources = [
            {
                "title": match.metadata.get("title", "Unknown"),
                "source": match.metadata.get("source", "Unknown"),
                "text": match.metadata.get("text", ""),
                "score": match.score,
                "tags": match.metadata.get("tags", []),
                "metadata": {
                    "all_traditions": match.metadata.get("all_traditions", []),
                    "all_teachers": match.metadata.get("all_teachers", []),
                    "all_chakras": match.metadata.get("all_chakras", []),
                    "all_12_steps": match.metadata.get("all_12_steps", []),
                    "all_ascension_paths": match.metadata.get("all_ascension_paths", []),
                    "primary_theme": match.metadata.get("primary_theme", ""),
                    "consciousness_level": match.metadata.get("consciousness_level", ""),
                }
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


@app.get("/verify-tagging")
async def verify_tagging():
    """
    Verify which tagging passes have been applied to documents
    
    Returns:
        Statistics showing:
        - Total documents
        - Documents with Pass 1 (keyword tags) - should be 100%
        - Documents with Pass 2 (AI enhancement - primary_theme) - Ollama/OpenAI
        - Documents with Pass 3 (Claude analysis) - not stored yet, would need separate tracking
    """
    try:
        # Query Pinecone to get sample of documents
        query_vector = [0.0] * PINECONE_DIMENSION
        results = index.query(
            vector=query_vector,
            top_k=10000,  # Get all documents
            include_metadata=True
        )
        
        if not results.matches:
            return {
                "status": "success",
                "message": "No documents found in database",
                "total_documents": 0
            }
        
        # Group by title and analyze tagging
        documents_dict = {}
        total_chunks = len(results.matches)
        
        for match in results.matches:
            title = match.metadata.get('title', 'Unknown')
            
            if title not in documents_dict:
                documents_dict[title] = {
                    'title': title,
                    'chunk_count': 0,
                    'has_keyword_tags': False,
                    'has_ai_enhancement': False,
                    'sample_tags': [],
                    'sample_primary_theme': None,
                    'sample_categories': {}
                }
            
            doc = documents_dict[title]
            doc['chunk_count'] += 1
            
            # Check Pass 1: Keyword tags (should always exist)
            tags = match.metadata.get('tags', [])
            if tags and len(tags) > 0:
                doc['has_keyword_tags'] = True
                if not doc['sample_tags']:
                    doc['sample_tags'] = tags[:10]  # First 10 tags
            
            # Check Pass 2: AI enhancement (primary_theme indicates Ollama/OpenAI was used)
            primary_theme = match.metadata.get('primary_theme', '')
            if primary_theme:
                doc['has_ai_enhancement'] = True
                if not doc['sample_primary_theme']:
                    doc['sample_primary_theme'] = primary_theme
            
            # Sample categories
            if not doc['sample_categories']:
                doc['sample_categories'] = {
                    'chakras': match.metadata.get('all_chakras', [])[:3],
                    'traditions': match.metadata.get('all_traditions', [])[:3],
                    'teachers': match.metadata.get('all_teachers', [])[:3],
                    'consciousness_level': match.metadata.get('consciousness_level', '')
                }
        
        # Calculate statistics
        total_docs = len(documents_dict)
        docs_with_keywords = sum(1 for d in documents_dict.values() if d['has_keyword_tags'])
        docs_with_ai = sum(1 for d in documents_dict.values() if d['has_ai_enhancement'])
        
        # Sample a few documents for detailed view
        sample_docs = list(documents_dict.values())[:5]
        
        return {
            "status": "success",
            "summary": {
                "total_documents": total_docs,
                "total_chunks": total_chunks,
                "pass_1_keyword_tags": {
                    "count": docs_with_keywords,
                    "percentage": round((docs_with_keywords / total_docs * 100) if total_docs > 0 else 0, 1),
                    "status": "✅ All documents tagged" if docs_with_keywords == total_docs else f"⚠️ {total_docs - docs_with_keywords} missing tags"
                },
                "pass_2_ai_enhancement": {
                    "count": docs_with_ai,
                    "percentage": round((docs_with_ai / total_docs * 100) if total_docs > 0 else 0, 1),
                    "status": "✅ All enhanced" if docs_with_ai == total_docs else f"ℹ️ {total_docs - docs_with_ai} without AI enhancement (Ollama/OpenAI)"
                },
                "pass_3_claude_analysis": {
                    "count": 0,
                    "percentage": 0,
                    "status": "ℹ️ Run 'Claude Deep Analysis' button to apply",
                    "note": "Claude analysis finds cross-document connections and is separate from upload tagging"
                }
            },
            "sample_documents": sample_docs
        }
        
    except Exception as e:
        logger.error(f"Tagging verification failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/retag-documents")
async def retag_documents(request: RetagRequest):
    """
    Re-tag existing documents with AI enhancement (Pass 2)
    
    This endpoint:
    1. Retrieves existing document chunks from Pinecone
    2. Re-runs tagging with AI enhancement enabled (Ollama or OpenAI)
    3. Updates metadata in Pinecone with enhanced tags
    
    Args:
        document_titles: List of document titles to re-tag (None/empty = all documents)
        ai_provider: "ollama" (FREE) or "openai" (paid)
        ollama_model: Ollama model to use (default: "llama3.1")
        batch_size: Number of chunks to process at once (default: 50)
    
    Returns:
        Status with counts of documents and chunks processed
    """
    try:
        ai_provider = request.ai_provider or "ollama"
        ollama_model = request.ollama_model or "llama3.1"
        batch_size = request.batch_size or 50
        
        logger.info(f"Starting re-tagging with AI provider: {ai_provider}")
        
        # Query Pinecone to get all chunks
        query_vector = [0.0] * PINECONE_DIMENSION
        
        if request.document_titles and len(request.document_titles) > 0:
            # Filter by specific titles
            all_matches = []
            for title in request.document_titles:
                results = index.query(
                    vector=query_vector,
                    top_k=10000,
                    include_metadata=True,
                    filter={"title": title}
                )
                all_matches.extend(results.matches)
            matches = all_matches
        else:
            # Get all documents
            results = index.query(
                vector=query_vector,
                top_k=10000,
                include_metadata=True
            )
            matches = results.matches
        
        if not matches:
            return {
                "status": "success",
                "message": "No documents found to re-tag",
                "documents_processed": 0,
                "chunks_processed": 0
            }
        
        # Group by document title
        documents_dict = {}
        for match in matches:
            title = match.metadata.get('title', 'Unknown')
            if title not in documents_dict:
                documents_dict[title] = []
            documents_dict[title].append(match)
        
        total_docs = len(documents_dict)
        total_chunks = len(matches)
        processed_chunks = 0
        updated_chunks = 0
        failed_chunks = 0
        
        logger.info(f"Found {total_docs} documents with {total_chunks} total chunks")
        
        # Process in batches
        vectors_to_update = []
        
        for doc_title, doc_matches in documents_dict.items():
            logger.info(f"Processing document: {doc_title} ({len(doc_matches)} chunks)")
            
            for match in doc_matches:
                try:
                    chunk_text = match.metadata.get('text', '')
                    if not chunk_text:
                        logger.warning(f"Skipping chunk {match.id} - no text found")
                        continue
                    
                    # Re-generate tags with AI enhancement
                    tags = generate_tags(
                        chunk_text,
                        use_ai=True,  # Enable AI enhancement
                        ai_provider=ai_provider,
                        title=doc_title,
                        ollama_model=ollama_model
                    )
                    
                    # Get existing metadata
                    existing_metadata = match.metadata.copy()
                    
                    # Extract detected_categories for flattening
                    detected_cats = tags.get("detected_categories", {})
                    
                    # Update metadata with enhanced tags
                    updated_metadata = {
                        **existing_metadata,  # Keep existing fields
                        
                        # Update core tags
                        "tags": tags.get("tags", existing_metadata.get("tags", [])),
                        "primary_theme": tags.get("primary_theme", existing_metadata.get("primary_theme", "")),
                        "consciousness_level": tags.get("consciousness_level", existing_metadata.get("consciousness_level", "")),
                        "emotions": tags.get("emotions", existing_metadata.get("emotions", [])),
                        
                        # Update primary fields
                        "primary_chakra": tags.get("primary_chakra", existing_metadata.get("primary_chakra", "")),
                        "tradition": tags.get("tradition", existing_metadata.get("tradition", "")),
                        "teacher": tags.get("teacher", existing_metadata.get("teacher", "")),
                        "ascension_path": tags.get("ascension_path", existing_metadata.get("ascension_path", "")),
                        "bridge_concept": tags.get("bridge_concept", existing_metadata.get("bridge_concept", "")),
                        "recovery_focus": tags.get("recovery_focus", existing_metadata.get("recovery_focus", "")),
                        "healing_modality": tags.get("healing_modality", existing_metadata.get("healing_modality", "")),
                        
                        # Update comprehensive fields
                        "all_chakras": detected_cats.get("chakras", existing_metadata.get("all_chakras", [])),
                        "all_meridians": detected_cats.get("meridians", existing_metadata.get("all_meridians", [])),
                        "all_12_steps": detected_cats.get("twelve_steps", existing_metadata.get("all_12_steps", [])),
                        "all_consciousness_levels": detected_cats.get("consciousness_level", existing_metadata.get("all_consciousness_levels", [])),
                        "all_traditions": detected_cats.get("traditions", existing_metadata.get("all_traditions", [])),
                        "all_teachers": detected_cats.get("teachers", existing_metadata.get("all_teachers", [])),
                        "all_quantum_physics": detected_cats.get("quantum_science", existing_metadata.get("all_quantum_physics", [])),
                        "all_quantum_particles": detected_cats.get("quantum_particles", existing_metadata.get("all_quantum_particles", [])),
                        "all_ascension_paths": detected_cats.get("ascension_paths", existing_metadata.get("all_ascension_paths", [])),
                        "all_bridge_concepts": detected_cats.get("bridge_concepts", existing_metadata.get("all_bridge_concepts", [])),
                        "all_universal_laws": detected_cats.get("universal_laws", existing_metadata.get("all_universal_laws", [])),
                        "all_healing_modalities": detected_cats.get("healing_modalities", existing_metadata.get("all_healing_modalities", [])),
                        "all_sacred_geometry": detected_cats.get("sacred_geometry", existing_metadata.get("all_sacred_geometry", [])),
                        "all_subtle_bodies": detected_cats.get("subtle_bodies", existing_metadata.get("all_subtle_bodies", [])),
                        "all_addiction_types": detected_cats.get("addiction_type", existing_metadata.get("all_addiction_types", []))
                    }
                    
                    # Add program_level if detected
                    if "program_level" in tags:
                        updated_metadata["program_level"] = tags["program_level"]
                    
                    # Clean metadata for Pinecone
                    updated_metadata = clean_metadata_for_pinecone(updated_metadata)
                    
                    # Get the existing embedding (we don't regenerate it)
                    # We need to fetch it from Pinecone or keep the existing vector
                    # For now, we'll need to query to get the vector, or we can just update metadata
                    # Actually, we can use fetch to get the vectors
                    
                    vectors_to_update.append({
                        "id": match.id,
                        "metadata": updated_metadata
                    })
                    
                    processed_chunks += 1
                    
                    # Update in batches
                    if len(vectors_to_update) >= batch_size:
                        # Fetch existing vectors to preserve embeddings
                        ids_to_fetch = [v["id"] for v in vectors_to_update]
                        fetched = index.fetch(ids=ids_to_fetch)
                        
                        # Prepare vectors with existing embeddings + updated metadata
                        vectors_with_embeddings = []
                        for vec_update in vectors_to_update:
                            vec_id = vec_update["id"]
                            if vec_id in fetched.vectors:
                                existing_vector = fetched.vectors[vec_id]
                                vectors_with_embeddings.append({
                                    "id": vec_id,
                                    "values": existing_vector.values,  # Keep existing embedding
                                    "metadata": vec_update["metadata"]
                                })
                        
                        if vectors_with_embeddings:
                            index.upsert(vectors=vectors_with_embeddings)
                            updated_chunks += len(vectors_with_embeddings)
                            logger.info(f"Updated batch: {len(vectors_with_embeddings)} chunks")
                        
                        vectors_to_update = []
                
                except Exception as chunk_error:
                    logger.error(f"Error processing chunk {match.id}: {chunk_error}")
                    failed_chunks += 1
                    continue
        
        # Process remaining vectors
        if vectors_to_update:
            ids_to_fetch = [v["id"] for v in vectors_to_update]
            fetched = index.fetch(ids=ids_to_fetch)
            
            vectors_with_embeddings = []
            for vec_update in vectors_to_update:
                vec_id = vec_update["id"]
                if vec_id in fetched.vectors:
                    existing_vector = fetched.vectors[vec_id]
                    vectors_with_embeddings.append({
                        "id": vec_id,
                        "values": existing_vector.values,
                        "metadata": vec_update["metadata"]
                    })
            
            if vectors_with_embeddings:
                index.upsert(vectors=vectors_with_embeddings)
                updated_chunks += len(vectors_with_embeddings)
        
        logger.info(f"Re-tagging complete: {updated_chunks} chunks updated, {failed_chunks} failed")
        
        return {
            "status": "success",
            "message": f"Re-tagged {total_docs} documents",
            "documents_processed": total_docs,
            "chunks_processed": processed_chunks,
            "chunks_updated": updated_chunks,
            "chunks_failed": failed_chunks,
            "ai_provider": ai_provider
        }
        
    except Exception as e:
        logger.error(f"Re-tagging failed: {e}")
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


@app.post("/analyze-documents")
async def analyze_documents(request: AnalyzeRequest):
    """
    Run Claude second-pass analysis on documents in batches with budget enforcement.
    """
    try:
        analysis_type = request.analysis_type or "recent"
        limit = request.limit or 50
        filters = request.filters
        selected_titles = request.selected_titles or []

        # Retrieve documents from Pinecone
        query_vector = [0.0] * PINECONE_DIMENSION
        matches = []

        if analysis_type == "recent":
            results = index.query(
                vector=query_vector,
                top_k=min(limit, 10000),
                include_metadata=True
            )
            matches = results.matches
        elif analysis_type == "full":
            results = index.query(
                vector=query_vector,
                top_k=10000,
                include_metadata=True
            )
            matches = results.matches
        elif analysis_type == "theme":
            results = index.query(
                vector=query_vector,
                top_k=10000,
                include_metadata=True,
                filter=filters or {}
            )
            matches = results.matches
        elif analysis_type == "selected":
            if not selected_titles:
                raise HTTPException(status_code=400, detail="selected_titles required for selected analysis_type")
            for title in selected_titles:
                partial = index.query(
                    vector=query_vector,
                    top_k=min(limit, 500),
                    include_metadata=True,
                    filter={"title": title}
                )
                matches.extend(partial.matches)
        else:
            raise HTTPException(status_code=400, detail="Invalid analysis_type")

        documents = [
            {
                "id": match.id,
                "text": match.metadata.get("text", ""),
                "tags": match.metadata.get("tags", []),
                "title": match.metadata.get("title", "Unknown")
            }
            for match in matches if match and getattr(match, "metadata", None)
        ]

        if not documents:
            return {
                "status": "success",
                "message": "No documents found to analyze",
                "documents_found": 0
            }

        # Estimate cost using existing estimator
        estimate = estimate_claude_cost([{"metadata": m.metadata} for m in matches], batch_size=15)

        budget_ok = spending_tracker.can_afford(estimate.get("total_cost", 0))
        if not budget_ok.get("can_afford", True):
            return {
                "status": "budget_exceeded",
                "estimate": estimate,
                "budget": budget_ok
            }

        # Run analysis in batches of 15 documents
        batch_size = 15
        batch_results = []
        for start in range(0, len(documents), batch_size):
            batch_docs = documents[start:start + batch_size]
            analysis = claude_second_pass_analysis(batch_docs, batch_size=batch_size)
            batch_results.append({
                "batch_start": start,
                "batch_end": start + len(batch_docs) - 1,
                "documents_analyzed": len(batch_docs),
                "analysis": analysis
            })

        # Record spending
        spending_tracker.record_analysis({
            "analysis_type": analysis_type,
            "document_count": len(documents),
            "total_cost": estimate.get("total_cost", 0),
            "input_tokens": estimate.get("total_input_tokens", 0),
            "output_tokens": estimate.get("total_output_tokens", 0)
        })

        return {
            "status": "success",
            "analysis_type": analysis_type,
            "documents_analyzed": len(documents),
            "estimate": estimate,
            "batches": batch_results
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analyze documents failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
