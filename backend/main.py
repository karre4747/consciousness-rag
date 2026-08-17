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

from fastapi import FastAPI, HTTPException, Request, BackgroundTasks, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response
from starlette.middleware.base import BaseHTTPMiddleware
from pydantic import BaseModel
from contextlib import asynccontextmanager
from typing import List, Optional, Dict, Any
import asyncio
import logging
from datetime import datetime

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
# Global Clients
pinecone_client = None
openai_client = None
anthropic_client = None
index = None
spending_tracker = SpendingTracker()


# Configuration
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "evolve-consciousness")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-large")
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-5-20250929")
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1800"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))
PINECONE_DIMENSION = int(os.getenv("PINECONE_DIMENSION", "1536"))

# Import Database
import database

# Background Sync Status
SYNC_STATUS = {
    "status": "idle",  # idle | running | completed | error
    "total_vectors": 0,
    "processed_vectors": 0,
    "documents_found": 0,
    "current_document": None,
    "error": None,
    "last_updated": None
}

# Global task stop signal
TASK_STOP_SIGNAL = False

# Global re-tagging progress tracking
RETAG_STATUS = {
    "total_documents": 0,
    "processed_documents": 0,
    "status": "idle",  # idle | running | completed | error | stopped
    "error": None,
}

# Global analysis progress tracking
ANALYSIS_STATUS = {
    "total_documents": 0,
    "processed_documents": 0,
    "status": "idle",  # idle | running | completed | error | stopped
    "error": None,
    "last_updated": None
}


# Existing SYNC_STATUS remains for database sync


async def sync_database_with_pinecone():
    """
    Background task to populate SQLite from Pinecone.
    Non-blocking with detailed progress tracking.
    """
    global SYNC_STATUS, index
    
    # Prevent multiple concurrent syncs
    if SYNC_STATUS["status"] == "running":
        logger.info("Sync already running, skipping...")
        return
    
    # Reset status
    SYNC_STATUS.update({
        "status": "running",
        "total_vectors": 0,
        "processed_vectors": 0,
        "documents_found": 0,
        "current_document": None,
        "error": None,
        "last_updated": datetime.now().isoformat()
    })
    
    logger.info("🔄 Starting Database Sync...")
    
    try:
        import gc
        
        known_documents = {}  # Temp tracker for this run
        total_vectors_checked = 0
        documents_found = 0
        
        async def process_batch(batch_ids):
            nonlocal documents_found, total_vectors_checked
            try:
                # Fetch actual vector data
                fetched = await pinecone_with_retry(lambda: index.fetch(ids=batch_ids), max_retries=3)
                
                for vec in fetched.vectors.values():
                    title = vec.metadata.get('title', 'Unknown')
                    
                    if title not in known_documents:
                        known_documents[title] = {
                            "count": 0,
                            "tags": False,
                            "provider": None,
                            "is_analyzed": False,
                            "schema_version": 2 # Default to 2 for modern sync
                        }
                        documents_found += 1
                        SYNC_STATUS["documents_found"] = documents_found
                        SYNC_STATUS["current_document"] = title
                    
                    known_documents[title]["count"] += 1
                    md = vec.metadata
                    
                    # Update schema version if present in any chunk
                    ver = md.get('schema_version')
                    if ver:
                        try:
                            known_documents[title]["schema_version"] = int(ver)
                        except (ValueError, TypeError):
                            pass
                    
                    # Check tags
                    tags = md.get('tags', [])
                    if tags:
                        known_documents[title]["tags"] = True
                        # Check for analysis in tags
                        if isinstance(tags, list):
                            for t in tags:
                                if "analyzed" in str(t).lower() or "claude" in str(t).lower():
                                    known_documents[title]["is_analyzed"] = True
                    
                    # Check provider
                    if md.get('ai_provider'):
                        known_documents[title]["provider"] = md.get('ai_provider')
                    
                    # Check explicit analysis markers
                    if md.get('primary_theme') or md.get('cross_document_themes') or md.get('patterns'):
                        known_documents[title]["is_analyzed"] = True
                
                logger.info(f"Syncing document: {title}")
                # Incremental Save Logic
                for title, info in known_documents.items():
                    # Determine status hierarchy
                    status = "uploaded"
                    if info["provider"]:
                        status = "tagged"
                    if info["is_analyzed"]:
                        status = "analyzed"
                    
                    database.add_document(title, info["count"], info["tags"], schema_version=info["schema_version"])
                    if status != "uploaded":
                        database.update_status(title, status, info["provider"], schema_version=info["schema_version"])
                
                # Free memory
                gc.collect()
                
            except Exception as e:
                logger.error(f"Sync fetch error: {e}")
                raise
        
        # Stream IDs and process immediately
        def get_all_batches():
            return list(index.list())
        
        all_batches = await asyncio.to_thread(get_all_batches)
        
        # Calculate total for progress tracking
        total_batches = len(all_batches)
        SYNC_STATUS["total_vectors"] = sum(len(batch) for batch in all_batches if batch)
        
        for batch_idx, ids_batch in enumerate(all_batches):
            if not ids_batch:
                continue
            
            await process_batch(ids_batch)
            total_vectors_checked += len(ids_batch)
            SYNC_STATUS["processed_vectors"] = total_vectors_checked
            SYNC_STATUS["last_updated"] = datetime.now().isoformat()
            
            if total_vectors_checked % 100 == 0:
                logger.info(f"📊 Sync progress: {total_vectors_checked}/{SYNC_STATUS['total_vectors']} vectors, {documents_found} documents")
                gc.collect()
                await asyncio.sleep(0.1)  # Yield to event loop
        
        SYNC_STATUS["status"] = "completed"
        SYNC_STATUS["last_updated"] = datetime.now().isoformat()
        logger.info(f"✅ Database Sync Complete! Processed {total_vectors_checked} vectors, found {documents_found} documents.")
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"❌ Sync failed: {error_msg}")
        SYNC_STATUS["status"] = "error"
        SYNC_STATUS["error"] = error_msg
        SYNC_STATUS["last_updated"] = datetime.now().isoformat()


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
        
        # Connect to index - get host for production performance
        # Using host instead of name avoids extra describe_index call
        index_desc = pinecone_client.describe_index(PINECONE_INDEX_NAME)
        index_host = index_desc.host
        index = pinecone_client.Index(host=index_host)
        logger.info(f"Connected to Pinecone index: {PINECONE_INDEX_NAME} (host: {index_host})")
        
        # Initialize OpenAI
        logger.info("Initializing OpenAI client...")
        openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Initialize Anthropic
        logger.info("Initializing Anthropic client...")
        anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        
        logger.info("All services initialized successfully!")
        
        # Initialize DB
        database.init_db()
        
        # Start background sync if empty (optional, user can trigger)
        # asyncio.create_task(sync_database_with_pinecone())
        
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

# Add CSP header middleware
class CSPMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "img-src 'self' data: https:; "
            "font-src 'self' data: https://fonts.gstatic.com; "
            "connect-src 'self' https://*;"
        )
        # Standard Security Headers
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response

app.add_middleware(CSPMiddleware)

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
    ollama_model: Optional[str] = "llama3.3"  # Ollama model to use


class QueryRequest(BaseModel):
    """Request model for RAG query"""
    question: str
    program_level: Optional[str] = None
    filters: Optional[Dict[str, Any]] = None
    top_k: Optional[int] = 15


class QueryResponse(BaseModel):
    """Response model for RAG query"""
    answer: str
    sources: List[Dict[str, Any]]
    metadata: Dict[str, Any]


class RetagRequest(BaseModel):
    """Request model for re-tagging existing documents"""
    document_titles: Optional[List[str]] = None  # None or empty = all documents
    ai_provider: Optional[str] = "ollama"  # "ollama" (FREE) or "openai" (paid)
    ollama_model: Optional[str] = "llama3.3"  # Ollama model to use
    batch_size: Optional[int] = 50  # Process chunks in batches


class AnalyzeRequest(BaseModel):
    """Request model for Claude deep analysis"""
    analysis_type: Optional[str] = "recent"  # "recent", "full", "selected"
    limit: Optional[int] = 50
    filters: Optional[Dict[str, Any]] = None
    selected_titles: Optional[List[str]] = None


class DuplicateCheckRequest(BaseModel):
    """Request model for checking duplicate documents"""
    title: str


# === HELPER FUNCTIONS ===

async def pinecone_with_retry(func, max_retries=3, base_delay=1, max_delay=60, timeout=30.0):
    """
    Execute Pinecone operation with exponential backoff retry and timeout.
    
    Only retries on:
    - 5xx server errors (500, 502, 503, 504)
    - 429 rate limiting
    - Timeout errors
    
    Does NOT retry on:
    - 4xx client errors (400, 401, 403, 404)
    """
    import random
    from pinecone.exceptions import PineconeException
    
    for attempt in range(max_retries):
        try:
            return await asyncio.wait_for(
                asyncio.to_thread(func),
                timeout=timeout
            )
        except asyncio.TimeoutError:
            if attempt == max_retries - 1:
                raise  # Re-raise TimeoutError so endpoint handlers can catch it
            delay = min(base_delay * (2 ** attempt), max_delay)
            jitter = random.uniform(0, delay * 0.1)
            logger.warning(f"Pinecone timeout, retrying in {delay + jitter:.2f}s (attempt {attempt + 1}/{max_retries})")
            await asyncio.sleep(delay + jitter)
        except PineconeException as e:
            status_code = getattr(e, 'status', None)
            
            # Don't retry client errors (except 429)
            if status_code and status_code < 500 and status_code != 429:
                raise
            
            # Last attempt - re-raise
            if attempt == max_retries - 1:
                raise
            
            # Retry on 5xx, 429, or None (transient errors like connection issues)
            if status_code is None or status_code >= 500 or status_code == 429:
                delay = min(base_delay * (2 ** attempt), max_delay)
                jitter = random.uniform(0, delay * 0.1)
                logger.warning(f"Pinecone error {status_code}, retrying in {delay + jitter:.2f}s (attempt {attempt + 1}/{max_retries})")
                await asyncio.sleep(delay + jitter)
            else:
                raise
        except Exception as e:
            # Non-Pinecone exceptions - don't retry
            raise


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
    total_context_chars = 0
    MAX_CONTEXT_CHARS = 8000  # Limit context to ~2000 tokens for faster processing
    
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
            # Truncate individual chunks to 1500 chars max
            truncated_text = text[:1500] + "..." if len(text) > 1500 else text
            # Include source subtly to allow the AI to synthesize without prefixing every sentence with 'According to...'
            chunk_text = f"---\n{truncated_text}\n(Library Note: {title})\n---"
            
            # Stop adding context if we exceed limit
            if total_context_chars + len(chunk_text) > MAX_CONTEXT_CHARS:
                break
                
            context_parts.append(chunk_text)
            total_context_chars += len(chunk_text)
    
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

Provide a comprehensive, authoritative, yet compassionate answer that:
1. Speaks as a single, unified voice of wisdom—the voice of the Evolve Consciousness Engine.
2. Synthesizes the information from the provided context into a cohesive whole. 
3. Avoids phrases like "According to the source" or "One document says." Instead, present the knowledge as an integrated truth.
4. Offers practical, direct application or next steps for the user's life.
5. Maintains the appropriate depth for the {program_level} level without unnecessary technical citations.

ANSWER:"""

    try:
        # Switch to OpenAI due to Anthropic billing issue
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000
        )
        return response.choices[0].message.content
        
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
            "Expires": "0"
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
async def health_check():
    """Detailed health check"""
    try:
        # Check Pinecone with timeout to prevent hanging
        try:
            stats = await pinecone_with_retry(
                index.describe_index_stats,
                max_retries=2,
                base_delay=0.5,
                timeout=5.0
            )
            
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
        except asyncio.TimeoutError:
            logger.error("Health check timed out - Pinecone may be slow or unresponsive")
            return {
                "status": "degraded",
                "pinecone": {
                    "connected": False,
                    "error": "Timeout - Pinecone not responding"
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


@app.get("/sync-status")
async def get_sync_status():
    """Get the current status of the database sync process"""
    return {
        "sync_status": SYNC_STATUS,
        "message": "Sync status retrieved successfully"
    }


@app.post("/sync-trigger")
async def trigger_sync(background_tasks: BackgroundTasks):
    """Manually trigger a database sync from Pinecone to SQLite"""
    if SYNC_STATUS["status"] == "running":
        return {
            "status": "already_running",
            "message": "Sync is already in progress",
            "sync_status": SYNC_STATUS
        }
    
    # Start sync in background
    background_tasks.add_task(sync_database_with_pinecone)
    
    return {
        "status": "started",
        "message": "Database sync started in background. Check /sync-status for progress.",
        "sync_status": SYNC_STATUS
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
        BATCH_SIZE = 20  # Reduced from 50 to prevent Pinecone 429 errors
        total_uploaded = 0

        for batch_start in range(0, total_chunks, BATCH_SIZE):
            batch_end = min(batch_start + BATCH_SIZE, total_chunks)
            batch_chunks = chunks[batch_start:batch_end]

            logger.info(f"Processing batch {batch_start}-{batch_end} of {total_chunks}")
            
            # Rate limiting pause between batches
            if total_uploaded > 0:
                await asyncio.sleep(0.5)

            vectors_to_upsert = []

            for i, chunk in enumerate(batch_chunks):
                chunk_index = batch_start + i

                try:
                    # Clean chunk text to ensure UTF-8 compatibility
                    clean_chunk = clean_text_for_metadata(chunk)

                    # Generate embedding
                    embedding = generate_embedding(clean_chunk)

                    # Generate tags (pass title for program_level detection and AI provider)
                    tags = await generate_tags(
                        clean_chunk,
                        use_ai=request.use_ai_tagging,
                        ai_provider=request.ai_provider,
                        title=request.title,
                        ollama_model=request.ollama_model,
                        openai_client=openai_client
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
                        "ai_provider": tags.get("ai_provider", ""),
                        "ai_model": tags.get("ai_model", ""),

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
                        "all_addiction_types": detected_cats.get("addiction_type", []),
                        "all_planets": detected_cats.get("planets", []),
                        "all_zodiac_signs": detected_cats.get("zodiac_signs", []),
                        
                        # High Performance Markers
                        "schema_version": 2,
                        "chunk_size": CHUNK_SIZE
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
                    await pinecone_with_retry(
                        lambda v=vectors_to_upsert: index.upsert(vectors=v),
                        max_retries=3,
                        timeout=20.0
                    )
                    total_uploaded += len(vectors_to_upsert)
                    logger.info(f"Uploaded batch: {len(vectors_to_upsert)} vectors (total: {total_uploaded}/{total_chunks})")
                except Exception as upsert_error:
                    logger.error(f"Error upserting batch: {upsert_error}")
                    raise HTTPException(status_code=500, detail=f"Failed to upload batch: {str(upsert_error)}")

        if total_uploaded > 0:
             # Add to local SQLite database so it appears in UI
             has_tags = False
             ai_provider = None
             if 'tags' in locals() and isinstance(tags, dict):
                 has_tags = bool(tags.get("tags"))
                 ai_provider = tags.get("ai_provider")
             
             database.add_document(request.title, total_chunks, has_tags, ai_provider=ai_provider, schema_version=2)
             logger.info(f"Added {request.title} to local SQLite database")

        return {
            "status": "success",
            "message": f"Document '{request.title}' processed successfully",
            "chunks_created": total_chunks,
            "vectors_uploaded": total_uploaded
        }

    except asyncio.TimeoutError:
        logger.error("Upload timed out waiting for Pinecone")
        raise HTTPException(status_code=504, detail="Upload timed out - please try again")
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/upload-file")
async def upload_file(
    file: UploadFile = File(...),
    use_ai_tagging: bool = Form(False),
    ai_provider: str = Form("openai"),
    ollama_model: str = Form("llama3.3")
):
    """
    Upload a file (PDF, DOCX, TXT) and process it
    """
    try:
        logger.info(f"Uploading file: {file.filename}")
        
        # Read file content
        content = await file.read()
        
        # Extract text based on file type
        filename_lower = file.filename.lower()
        if filename_lower.endswith('.pdf'):
            import pypdf
            import io
            pdf_reader = pypdf.PdfReader(io.BytesIO(content))
            text = ""
            for page in pdf_reader.pages:
                text_content = page.extract_text()
                if text_content:
                    text += text_content + "\n"
        elif filename_lower.endswith('.docx'):
            import docx
            import io
            doc = docx.Document(io.BytesIO(content))
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        elif filename_lower.endswith(('.txt', '.md', '.markdown', '.csv')):
            try:
                text = content.decode('utf-8')
            except UnicodeDecodeError:
                # Fallback for other encodings
                text = content.decode('latin-1')
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {file.filename}")
        
        # Use the existing upload logic
        upload_request = UploadRequest(
            title=file.filename,
            source=file.filename,
            text=text,
            use_ai_tagging=use_ai_tagging,
            ai_provider=ai_provider,
            ollama_model=ollama_model
        )
        
        return await upload_document(upload_request)
        
    except Exception as e:
        logger.error(f"File upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))



@app.post("/query", response_model=QueryResponse)
async def query_knowledge(request: QueryRequest):
    """
    Query the knowledge base using RAG via domain-specific agents.
    """
    try:
        logger.info(f"Processing query: {request.question}")

        # Validate and clamp top_k to prevent slow queries. Defaults to 15:
        # cross-domain synthesis needs passages from several works, and 5 is
        # too thin to braid traditions.
        requested_top_k = request.top_k or 15
        top_k = max(1, min(25, requested_top_k))
        
        # Build filter focus
        raw_filters = request.filters or {}
        focus = ""
        if "focus_area" in raw_filters:
            focus = raw_filters["focus_area"]
            
        # Map legacy frontend filter values to new agent names
        if focus == "12-step":
            focus = "recovery"
        elif focus in ["mystical", "chakras"]:
            focus = "spiritual"
        elif focus == "astrology":
            focus = "metaphysics"
        elif focus == "":
            focus = "synthesis"

        # Import specialist agents
        from agents import RecoveryAgent, MetaphysicsAgent, ScienceAgent, TherapyAgent, SynthesisAgent, SponsorAgent, SpiritualAgent
        
        # Instantiate agent based on focus area
        if focus == "recovery":
            agent = RecoveryAgent()
        elif focus == "sponsor":
            agent = SponsorAgent()
        elif focus == "metaphysics":
            agent = MetaphysicsAgent()
        elif focus == "spiritual":
            agent = SpiritualAgent()
        elif focus == "science":
            agent = ScienceAgent()
        elif focus == "therapy":
            agent = TherapyAgent()
        else:
            agent = SynthesisAgent()

        # Run agent query in a thread pool to avoid blocking async event loop
        result = await asyncio.to_thread(agent.query, request.question, top_k=top_k)
        
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["answer"])
            
        matches = result.get("citations", [])
        
        # Format sources with full text and metadata for UI display
        sources = [
            {
                "title": match.get("title", "Unknown"),
                "source": match.get("metadata", {}).get("source", "Unknown"),
                "text": match.get("text", ""),
                "score": match.get("score", 0.0),
                "tags": match.get("tags", []),
                "metadata": {
                    "all_traditions": match.get("metadata", {}).get("all_traditions", []),
                    "all_teachers": match.get("metadata", {}).get("all_teachers", []),
                    "all_chakras": match.get("metadata", {}).get("all_chakras", []),
                    "all_12_steps": match.get("metadata", {}).get("all_12_steps", []),
                    "all_ascension_paths": match.get("metadata", {}).get("all_ascension_paths", []),
                    "all_planets": match.get("metadata", {}).get("all_planets", []),
                    "all_zodiac_signs": match.get("metadata", {}).get("all_zodiac_signs", []),
                    "primary_theme": match.get("metadata", {}).get("primary_theme", ""),
                    "consciousness_level": match.get("metadata", {}).get("consciousness_level", ""),
                }
            }
            for match in matches
        ]
        
        return QueryResponse(
            answer=result["answer"],
            sources=sources,
            metadata={
                "matches_found": len(matches),
                "program_level": request.program_level or "beginner",
                "model": "gpt-4o",
                "agent": agent.name
            }
        )
        
    except asyncio.TimeoutError:
        logger.error("Query timed out waiting for Pinecone")
        raise HTTPException(status_code=504, detail="Query timed out - please try again")
    except Exception as e:
        logger.error(f"Query failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats")
async def get_stats():
    """Get database statistics"""
    try:
        stats = await pinecone_with_retry(
            index.describe_index_stats,
            max_retries=2,
            timeout=10.0
        )

        # Build response - skip namespaces as it's not easily serializable
        response = {
            "index_name": PINECONE_INDEX_NAME,
            "total_vectors": stats.total_vector_count,
            "dimension": PINECONE_DIMENSION
        }
        
        # Try to add namespaces count if available
        # Try to add namespaces count if available
        if hasattr(stats, 'namespaces'):
            try:
                # Return the actual namespaces dict to debug where vectors are hiding
                if isinstance(stats.namespaces, dict):
                    # Convert to simple dict if it's a specific Pinecone object
                    response["namespaces"] = {k: v.vector_count for k, v in stats.namespaces.items()}
                elif stats.namespaces:
                    response["namespaces_raw"] = str(stats.namespaces)
            except Exception as e:
                response["namespaces_error"] = str(e)
        
        return response
    except asyncio.TimeoutError:
        logger.error("Stats retrieval timed out")
        raise HTTPException(status_code=504, detail="Pinecone query timed out")
    except Exception as e:
        logger.error(f"Stats retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# === DOCUMENT MANAGEMENT ENDPOINTS ===

@app.get("/uploaded-documents")
async def get_uploaded_documents():
    """
    Get list of all unique documents currently in Pinecone
    
    FIXED: Now uses list_paginated to retrieve ALL vectors, not just top_k=10000
    This ensures consistent document counts regardless of total chunk count.

    Returns:
        List of documents with titles, chunk counts
    """
    try:
        # First, get total vector count to determine if we need pagination
        stats = await pinecone_with_retry(
            index.describe_index_stats,
            max_retries=2,
            timeout=10.0
        )
        
        total_vectors = stats.total_vector_count
        logger.info(f"Total vectors in index: {total_vectors}")
        
        # Group by title to get unique documents
        documents_dict = {}
        
        if total_vectors == 0:
            return {
                "status": "success",
                "total_documents": 0,
                "documents": []
            }
        
        # Use list_paginated to get ALL vectors (handles pagination automatically)
        # This is more efficient than query() for listing all vectors
        try:
            # Pinecone's list() returns an iterator that handles pagination
            all_vector_ids = []
            for ids in index.list(limit=10000):  # Fetch in batches of 10000
                all_vector_ids.extend(ids)
            
            logger.info(f"Retrieved {len(all_vector_ids)} vector IDs")
            
            # Fetch metadata for all vectors in batches
            FETCH_BATCH_SIZE = 1000  # Pinecone fetch limit
            for i in range(0, len(all_vector_ids), FETCH_BATCH_SIZE):
                batch_ids = all_vector_ids[i:i + FETCH_BATCH_SIZE]
                
                fetched = await pinecone_with_retry(
                    lambda: index.fetch(ids=batch_ids),
                    max_retries=2,
                    timeout=15.0
                )
                
                # Process fetched vectors
                for vec_id, vector_data in fetched.vectors.items():
                    metadata = vector_data.metadata
                    title = metadata.get('title', 'Unknown')
                    
                    if title not in documents_dict:
                        documents_dict[title] = {
                            'title': title,
                            'source': metadata.get('source', ''),
                            'chunk_count': 0,
                            'total_chunks': metadata.get('total_chunks', 0)
                        }
                    
                    documents_dict[title]['chunk_count'] += 1
                
                logger.info(f"Processed batch {i//FETCH_BATCH_SIZE + 1}: {len(batch_ids)} vectors")
        
        except Exception as list_error:
            # Fallback to query method if list() fails
            logger.warning(f"list() failed, falling back to query: {list_error}")
            
            # Use query as fallback (may be inconsistent for large datasets)
            query_vector = [0.1] * PINECONE_DIMENSION
            results = await pinecone_with_retry(
                lambda: index.query(
                    vector=query_vector,
                    top_k=1000,
                    include_metadata=True
                ),
                max_retries=2,
                timeout=30.0
            )
            
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
        
        logger.info(f"Found {len(doc_list)} unique documents")
        
        return {
            "status": "success",
            "total_documents": len(doc_list),
            "documents": doc_list,
            "total_vectors": total_vectors
        }

    except asyncio.TimeoutError:
        logger.error("Uploaded documents query timed out")
        raise HTTPException(status_code=504, detail="Pinecone query timed out - database may be large")
    except Exception as e:
        logger.error(f"Failed to get uploaded documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/check-duplicate")
async def check_duplicate(request: DuplicateCheckRequest):
    """
    Check if a document with this title already exists (with or without extension)

    Args:
        request: {"title": "document_name"}

    Returns:
        {"exists": bool, "chunk_count": int, "title": str, "providers": list}
    """
    try:
        title = request.title
        base_title = title
        if '.' in title:
            base_title = title.rsplit('.', 1)[0]

        # 1. Check SQLite first (fastest and canonical)
        docs = database.get_all_documents()
        matching_doc = None
        for doc in docs:
            doc_title = doc.get("title", "")
            doc_base = doc_title.rsplit('.', 1)[0] if '.' in doc_title else doc_title
            
            # Compare lowercase base names or exact names
            if doc_title.lower() == title.lower() or doc_base.lower() == base_title.lower():
                matching_doc = doc
                break

        if matching_doc:
            logger.info(f"Duplicate check matched SQLite: {matching_doc['title']}")
            return {
                "status": "success",
                "exists": True,
                "chunk_count": matching_doc.get("chunk_count", 0),
                "title": matching_doc["title"],
                "providers": [matching_doc.get("ai_provider")] if matching_doc.get("ai_provider") else []
            }

        # 2. Fallback/Double-check Pinecone with candidate titles using $in operator
        candidate_titles = [
            base_title,
            base_title + ".pdf",
            base_title + ".docx",
            base_title + ".txt",
            base_title + ".md",
            title
        ]
        # De-duplicate list
        candidate_titles = list(set(candidate_titles))

        query_vector = [0.1] * PINECONE_DIMENSION
        results = await pinecone_with_retry(
            lambda: index.query(
                vector=query_vector,
                top_k=100,
                include_metadata=True,
                filter={"title": {"$in": candidate_titles}}
            ),
            max_retries=2,
            timeout=10.0
        )

        exists = len(results.matches) > 0
        chunk_count = len(results.matches) if exists else 0
        found_title = results.matches[0].metadata.get('title', title) if exists else title
        
        providers = []
        if exists:
            for m in results.matches:
                p = m.metadata.get('ai_provider')
                if p and p not in providers:
                    providers.append(p)

        return {
            "status": "success",
            "exists": exists,
            "chunk_count": chunk_count,
            "title": found_title,
            "providers": providers
        }

    except asyncio.TimeoutError:
        logger.error("Duplicate check timed out")
        raise HTTPException(status_code=504, detail="Duplicate check timed out - please try again")
    except Exception as e:
        logger.error(f"Duplicate check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def check_ai_status(providers):
    """Determine AI processing status from provider list"""
    if not providers:
        return "Pending"
    if "OPENAI" in providers:
        return "OPENAI"
    if "OLLAMA" in providers:
        return "OLLAMA"
    return ", ".join(providers)


@app.get("/document-status")
async def get_document_status():
    """
    Unified Endpoint: Returns documents from SQLite DB.
    Zero-latency, no scanning.
    """
    docs = database.get_all_documents()
    stats = database.get_stats()
    
    # Format for frontend compatibility
    formatted = []
    for d in docs:
        formatted.append({
            "title": d['title'],
            "chunk_count": d['chunk_count'],
            "pass_1_status": "Complete" if d['has_keyword_tags'] else "Pending",
            "pass_2_status": d['ai_provider'] if d['ai_provider'] else "Pending",
            "pass_3_status": "Complete" if (d['status'] == 'analyzed' or d.get('analysis_results')) else "Pending",
            "raw_providers": [d['ai_provider']] if d['ai_provider'] else [],
            "schema_version": d.get('schema_version', 1)
        })
        
    return {
        "status": "success",
        "cache_status": "ready",
        "total_documents": len(docs),
        "total_vectors": 0, # Don't care anymore
        "documents": formatted,
        "sync_status": SYNC_STATUS
    }

@app.get("/sync-status")
async def get_sync_status():
    """Get the current status of the database sync"""
    return SYNC_STATUS

@app.post("/sync-db")
async def trigger_sync():
    """Manually trigger database sync from Pinecone"""
    # Run in background without blocking
    asyncio.create_task(sync_database_with_pinecone())
    return {"status": "started", "message": "Background sync started"}


@app.get("/verify-tagging")
async def verify_tagging(limit: int = 100, offset: int = 0):
    """Legacy compatibility"""
    return await get_document_status()


def process_vector_metadata(metadata, documents_dict):
    """Helper to process metadata for tagging verification"""
    title = metadata.get('title', 'Unknown')
    
    if title not in documents_dict:
        documents_dict[title] = {
            'title': title,
            'chunk_count': 0,
            'has_keyword_tags': False,
            'ai_providers': set(),
        }
    
    doc = documents_dict[title]
    doc['chunk_count'] += 1
    
    # Check Pass 1: Keywords
    tags = metadata.get('tags', [])
    if tags and len(tags) > 0:
        doc['has_keyword_tags'] = True
    
    # Check Pass 2: AI Provider
    provider = metadata.get('ai_provider')
    if provider:
        doc['ai_providers'].add(str(provider).upper())
        
    # Check for legacy primary_theme as fallback
    if not provider and metadata.get('primary_theme'):
        doc['ai_providers'].add("PARTIAL_AI")




async def run_retagging_task(document_titles_to_process: List[str], ai_provider: str, ollama_model: str, batch_size: int):
    """
    Background task to process tagging without blocking the API.
    Includes aggressive rate limiting and error handling.
    """
    try:
        total_docs = len(document_titles_to_process)
        # Initialize RETAG_STATUS tracking
        global RETAG_STATUS, TASK_STOP_SIGNAL
        TASK_STOP_SIGNAL = False # Reset on start
        
        RETAG_STATUS["total_documents"] = total_docs
        RETAG_STATUS["processed_documents"] = 0
        RETAG_STATUS["status"] = "running"
        RETAG_STATUS["error"] = None
        logger.info(f"Background Tagging Started: {total_docs} documents using {ai_provider}")
        
        processed_chunks = 0
        updated_chunks = 0
        failed_chunks = 0
        
        # Main Loop: Process one document at a time
        for title in document_titles_to_process:
            if TASK_STOP_SIGNAL:
                logger.info("Task stop signal received. Aborting re-tagging.")
                RETAG_STATUS["status"] = "stopped"
                break
            
            database.update_status(title, "processing", ai_provider.upper())
            try:
                # Get chunks for THIS document
                query_vector = [0.1] * PINECONE_DIMENSION
                results = await pinecone_with_retry(
                    lambda: index.query(
                        vector=query_vector,
                        top_k=500, 
                        include_metadata=True,
                        filter={"title": title}
                    ),
                    max_retries=2,
                    timeout=30.0
                )
                
                matches = results.matches
                if not matches:
                    continue
                    
                # BATCH PROCESSING LOGIC
                # Group chunks into batches of 5 for OpenAI
                BATCH_SIZE_API = 5
                
                chunk_batches = []
                for i in range(0, len(matches), BATCH_SIZE_API):
                    chunk_batches.append(matches[i:i+BATCH_SIZE_API])
                
                total_batches = len(chunk_batches)
                logger.info(f"Processing {title}: {len(matches)} chunks in {total_batches} batches")

                for b_idx, batch in enumerate(chunk_batches):
                    # Extract texts
                    texts = [m.metadata.get('text', '') for m in batch]
                    valid_indices = [i for i, t in enumerate(texts) if t]
                    valid_texts = [texts[i] for i in valid_indices]
                    
                    if not valid_texts:
                        continue
                        
                    try:
                        # Call Batch API (Rate Limited)
                        # We use the batch function mapped into tagging.py
                        import tagging
                        import datetime
                        
                        batch_results = []

                        if ai_provider == 'ollama':
                            # Process OLLAMA sequentially (per batch)
                            for text in valid_texts:
                                # Run in thread to avoid blocking loop
                                res = await asyncio.to_thread(tagging.generate_tags_ollama, text, model=ollama_model)
                                batch_results.append(res)
                        else:
                            # OpenAI Path
                            # Aggressive Delay for Rate Limits (5s = ~12 Requests/Min)
                            # This stays comfortably under most Tier 1 limits
                            await asyncio.sleep(5.0) 
                            
                            batch_results, usage_stats = await tagging.generate_tags_batch_openai(
                                valid_texts, 
                                openai_client, 
                                timeout=60.0
                            )

                            # Record OpenAI spending
                            if usage_stats.get("total_cost", 0) > 0:
                                spending_tracker.record_analysis({
                                    "analysis_type": "openai_tagging",
                                    "document_count": 0, # It's chunks, not full docs technically, but we track at chunk level here
                                    "chunk_count": len(valid_texts),
                                    "input_tokens": usage_stats.get("input_tokens", 0),
                                    "output_tokens": usage_stats.get("output_tokens", 0),
                                    "total_cost": usage_stats.get("total_cost", 0),
                                    "input_cost": usage_stats.get("input_cost", 0),
                                    "output_cost": usage_stats.get("output_cost", 0),
                                    "batch_count": 1,
                                    "duration_seconds": 0
                                })
                        
                        # Process results back into vectors
                        batch_vectors_to_update = []
                        
                        for i, result in enumerate(batch_results):
                            # Map back to original match
                            original_idx = valid_indices[i]
                            match = batch[original_idx]
                            
                            # Mix with keyword tags if AI failed or returned partial
                            # (We always run keyword tagging as baseline)
                            keyword_tags = tagging.generate_tags_keyword_based(valid_texts[i])
                            
                            # Merge tags
                            ai_tags_list = result.get("tags", [])
                            if isinstance(ai_tags_list, str): ai_tags_list = [ai_tags_list]
                            
                            merged_tags = list(set(keyword_tags["tags"] + ai_tags_list))
                            
                            existing_metadata = match.metadata.copy()
                            
                            updated_metadata = {
                                **existing_metadata,
                                "tags": merged_tags,
                                "primary_theme": result.get("primary_theme") or keyword_tags.get("primary_theme", ""),
                                "consciousness_level": result.get("consciousness_level") or keyword_tags.get("consciousness_level", ""),
                                # Standard fields...
                                "ai_provider": ai_provider,
                                "last_updated": datetime.datetime.now(datetime.timezone.utc).isoformat()
                            }
                            
                            updated_metadata = clean_metadata_for_pinecone(updated_metadata)
                            
                            batch_vectors_to_update.append({
                                "id": match.id,
                                "metadata": updated_metadata
                            })
                            
                        # Upsert this batch immediately
                        if batch_vectors_to_update:
                            # Fetch current vectors to keep values
                            ids = [v["id"] for v in batch_vectors_to_update]
                            fetched = await pinecone_with_retry(lambda: index.fetch(ids=ids), max_retries=2)
                            
                            final_upsert = []
                            for v in batch_vectors_to_update:
                                if v["id"] in fetched.vectors:
                                    final_upsert.append({
                                        "id": v["id"],
                                        "values": fetched.vectors[v["id"]].values, # Preserve embedding
                                        "metadata": v["metadata"]
                                    })
                                    
                            if final_upsert:
                                await pinecone_with_retry(lambda v=final_upsert: index.upsert(vectors=v), max_retries=3)
                                updated_chunks += len(final_upsert)
                                processed_chunks += len(final_upsert)
                                
                    except Exception as e:
                        logger.error(f"Batch {b_idx} failed: {e}")
                        failed_chunks += len(batch)
                        
                # Document complete
                # PRESERVE STATUS: If it was already analyzed, keep it analyzed.
                current_docs = database.get_all_documents()
                current_doc = next((d for d in current_docs if d['title'] == title), None)
                final_status = "tagged"
                # Force status to 'tagged' so it re-appears in "Analyze Pending" queue
                # This meets the user's requirement to "send it back through analysis"
                # STAMP WITH V2: Mark as Schema Version 2 (High Performance)
                final_status = "tagged"
                
                database.update_status(title, final_status, ai_provider.upper(), schema_version=2)
                logger.info(f"Retagged {title}: {len(matches)} chunks (Final Status: {final_status}, Schema: V2)")
                RETAG_STATUS["processed_documents"] += 1
                
            except Exception as e:
                logger.error(f"Failed to process document {title}: {e}")
                database.update_status(title, "error", ai_provider.upper())
                RETAG_STATUS["status"] = "error"
                RETAG_STATUS["error"] = str(e)
                # Continue to next document instead of crashing the whole task
                continue
                
        logger.info(f"Re-tagging complete: {total_docs} docs, {updated_chunks} chunks updated")
        RETAG_STATUS["status"] = "completed"
        # Reset to idle after a short delay to allow new jobs
        await asyncio.sleep(5)
        RETAG_STATUS["status"] = "idle"

    except Exception as e:
        logger.error(f"Background tagging task CRITICAL FAILURE: {e}")



@app.get("/retag-status")
async def get_retag_status():
    """Return current re‑tagging progress status."""
    return RETAG_STATUS

@app.post("/stop-tasks")
async def stop_tasks():
    """Emergency stop for all background tasks (AI re-analysis and tagging)."""
    global TASK_STOP_SIGNAL
    TASK_STOP_SIGNAL = True
    logger.warning("USER ISSUED EMERGENCY STOP SIGNAL FOR ALL TASKS.")
    return {"status": "success", "message": "Emergency stop signal sent. Tasks will abort at next checkpoint."}

@app.post("/retag-documents")
async def retag_documents(request: RetagRequest, background_tasks: BackgroundTasks):
    """
    Re-tag existing documents (Async Background Job).
    Returns immediately to prevent timeouts.
    """
    try:
        ai_provider = request.ai_provider or "ollama"

        ollama_model = request.ollama_model or "llama3.3"
        batch_size = request.batch_size or 50
        
        logger.info(f"Queueing re-tagging job for provider: {ai_provider}")
        
        # Determine which documents to process
        document_titles_to_process = []
        if request.document_titles and len(request.document_titles) > 0:
            document_titles_to_process = request.document_titles
        else:
            # Fetch ALL titles from SQLite
            all_docs = database.get_all_documents() 
            document_titles_to_process = [d["title"] for d in all_docs]
            
        if not document_titles_to_process:
             return {"status": "error", "message": "No documents found to re-tag"}

        # Spawn Background Task
        background_tasks.add_task(
            run_retagging_task,
            document_titles_to_process, 
            ai_provider, 
            ollama_model, 
            batch_size
        )
        
        return {
            "status": "success",
            "message": f"Started background re-tagging for {len(document_titles_to_process)} documents. Please check Status tab for progress.",
            "job_id": "async_tagging",
            "documents_queued": len(document_titles_to_process)
        }
    
    except Exception as e:
        logger.error(f"Failed to queue re-tagging: {e}")
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
        query_vector = [0.1] * PINECONE_DIMENSION
        results = await pinecone_with_retry(
            lambda: index.query(
                vector=query_vector,
                top_k=500,  # Get all chunks
                include_metadata=True,
                filter={"title": title}
            ),
            max_retries=2,
            timeout=30.0
        )

        ids_to_delete = [] # Initialize ids_to_delete
        if not results.matches:
            logger.info("No chunks found in Pinecone to delete")
        else:
            ids_to_delete = [m.id for m in results.matches]
            logger.info(f"Found {len(ids_to_delete)} chunks to delete for title: {title}")
            
            # Batch delete (Pinecone has a limit of 1000 IDs per request)
            BATCH_SIZE = 1000
            for i in range(0, len(ids_to_delete), BATCH_SIZE):
                batch_ids = ids_to_delete[i:i + BATCH_SIZE]
                await pinecone_with_retry(
                    lambda batch_ids=batch_ids: index.delete(ids=batch_ids),
                    max_retries=3,
                    timeout=30.0
                )
                logger.info(f"Deleted batch {i//BATCH_SIZE + 1} ({len(batch_ids)} chunks)")

        # Also remove from SQLite
        database.delete_document(title)
        
        logger.info(f"Deleted {len(ids_to_delete)} chunks of document '{title}'")

        return {
            "status": "success",
            "message": f"Deleted {len(ids_to_delete)} chunks of '{title}'",
            "chunks_deleted": len(ids_to_delete)
        }


    except asyncio.TimeoutError:
        logger.error(f"Delete timed out for '{title}'")
        raise HTTPException(status_code=504, detail="Delete operation timed out - please try again")
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
        breakdown = spending_tracker.get_spending_breakdown(month)

        # Calculate estimated pages from tokens
        total_pages = round(stats['total_input_tokens'] / 650) if stats['total_input_tokens'] else 0

        return {
            "status": "success",
            "stats": {
                **stats,
                "breakdown": breakdown,
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
        query_vector = [0.1] * PINECONE_DIMENSION

        if analysis_type == "recent":
            results = await pinecone_with_retry(
                lambda: index.query(
                    vector=query_vector,
                    top_k=min(limit, 500),
                    include_metadata=True
                ),
                max_retries=2,
                timeout=30.0
            )
        elif analysis_type == "full":
            results = await pinecone_with_retry(
                lambda: index.query(
                    vector=query_vector,
                    top_k=1000,  # Max reasonable pool for corpus-wide analysis
                    include_metadata=True
                ),
                max_retries=2,
                timeout=30.0
            )
        elif analysis_type == "theme":
            results = await pinecone_with_retry(
                lambda: index.query(
                    vector=query_vector,
                    top_k=500,
                    include_metadata=True,
                    filter=filters or {}
                ),
                max_retries=2,
                timeout=30.0
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

        estimate = estimate_claude_cost(documents, batch_size=5)

        # Check budget
        budget_check = spending_tracker.can_afford(estimate['total_cost'])

        return {
            "status": "success",
            "estimate": estimate,
            "budget": budget_check,
            "analysis_type": analysis_type
        }

    except asyncio.TimeoutError:
        logger.error("Cost estimation timed out waiting for Pinecone")
        raise HTTPException(status_code=504, detail="Cost estimation timed out - please try again")
    except Exception as e:
        logger.error(f"Cost estimation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def update_pinecone_connections(title: str, connected_docs: List[str]):
    """Update Pinecone vector metadata for all chunks of a document to store connected_docs"""
    try:
        logger.info(f"Updating Pinecone metadata for {title} with connections: {connected_docs}")
        query_vector = [0.1] * PINECONE_DIMENSION
        # Query Pinecone to get all chunks for this title
        results = await pinecone_with_retry(
            lambda: index.query(
                vector=query_vector,
                top_k=500,
                filter={"title": title},
                include_metadata=False
            ),
            max_retries=2,
            timeout=15.0
        )
        
        if results and results.matches:
            for match in results.matches:
                # Update metadata for each chunk ID
                # Pinecone index.update allows partial metadata update
                await pinecone_with_retry(
                    lambda: index.update(id=match.id, set_metadata={"connected_docs": connected_docs}),
                    max_retries=2,
                    timeout=10.0
                )
            logger.info(f"Successfully updated Pinecone metadata for {len(results.matches)} chunks of {title}")
    except Exception as e:
        logger.error(f"Failed to update Pinecone metadata for {title}: {e}")


async def run_analysis_task(documents: List[Dict[str, Any]], analysis_type: str, estimate: Dict[str, Any]):
    """
    Background task to run Claude analysis in batches.
    Updates status and saves results incrementally to avoid timeouts.
    """
    global ANALYSIS_STATUS, TASK_STOP_SIGNAL
    try:
        total_docs = len(documents)
        TASK_STOP_SIGNAL = False
        
        ANALYSIS_STATUS.update({
            "total_documents": total_docs,
            "processed_documents": 0,
            "status": "running",
            "error": None,
            "last_updated": datetime.now().isoformat()
        })
        
        logger.info(f"Background Analysis Started: {total_docs} documents")
        
        batch_size = 5
        unique_titles = set()
        
        for start in range(0, len(documents), batch_size):
            if TASK_STOP_SIGNAL:
                logger.info("Task stop signal received. Aborting analysis.")
                ANALYSIS_STATUS["status"] = "stopped"
                break
                
            batch_docs = documents[start:start + batch_size]
            
            # Update status to 'processing' before calling Claude
            for doc in batch_docs:
                title = doc.get("title", "Unknown")
                if title != "Unknown":
                    database.update_status(title, "processing")
            
            # Call Claude analysis (wrapped in to_thread)
            analysis = await asyncio.to_thread(claude_second_pass_analysis, batch_docs, batch_size=batch_size)
            
            # Check for errors in Claude's output
            if isinstance(analysis, dict) and "error" in analysis:
                logger.error(f"Claude analysis batch failed: {analysis['error']}")
                # Mark as tagged again so they can be retried
                for doc in batch_docs:
                    title = doc.get("title", "Unknown")
                    if title != "Unknown":
                        database.update_status(title, "tagged")
                continue
            
            # Save results and update status to 'analyzed' incrementally
            # Map of possible identifiers to actual document titles in the batch
            id_map = {}
            for idx, d in enumerate(batch_docs):
                d_title = d.get("title", "")
                if d_title:
                    # Map "DOC X" -> title
                    id_map[f"doc {idx + 1}"] = d_title
                    id_map[f"doc{idx + 1}"] = d_title
                    # Map lowercase title -> title
                    id_map[d_title.lower()] = d_title
                    # Map title without extension -> title
                    if '.' in d_title:
                        id_map[d_title.rsplit('.', 1)[0].lower()] = d_title

            # Helper function to resolve Claude's reference to actual document title
            def resolve_title(ref: str) -> str:
                if not ref:
                    return ""
                ref_clean = str(ref).strip().lower()
                # 1. Check exact/base name mapping
                if ref_clean in id_map:
                    return id_map[ref_clean]
                # 2. Check if ref is a substring of any doc title
                for d_title in id_map.values():
                    if ref_clean in d_title.lower() or d_title.lower() in ref_clean:
                        return d_title
                return ref

            # Normalize all connections in Claude's output
            normalized_connections = []
            for c in analysis.get("suggested_connections", []):
                doc_id_resolved = resolve_title(c.get("doc_id", ""))
                relates_to_resolved = resolve_title(c.get("relates_to", ""))
                connection_desc = c.get("connection", "")
                
                if doc_id_resolved and relates_to_resolved and doc_id_resolved != relates_to_resolved:
                    normalized_connections.append({
                        "doc_id": doc_id_resolved,
                        "relates_to": relates_to_resolved,
                        "connection": connection_desc
                    })

            for doc in batch_docs:
                title = doc.get("title", "Unknown")
                if title != "Unknown":
                    unique_titles.add(title)
                    logger.info(f"Marking document as analyzed and saving results: {title}")
                    
                    # Extract resolved connections for THIS document
                    doc_connections = [
                        {"relates_to": c["relates_to"] if c["doc_id"] == title else c["doc_id"], "connection": c["connection"]}
                        for c in normalized_connections
                        if c["doc_id"] == title or c["relates_to"] == title
                    ]
                    
                    # Prepare analysis results for this document
                    doc_analysis = {
                        "cross_document_themes": analysis.get("cross_document_themes", []),
                        "consciousness_patterns": analysis.get("consciousness_patterns", []),
                        "suggested_connections": doc_connections,
                        "synthesis_opportunities": analysis.get("synthesis_opportunities", []),
                        "analyzed_at": datetime.now().isoformat(),
                        "batch_info": {
                            "batch_size": len(batch_docs),
                            "analysis_type": analysis_type
                        }
                    }
                    
                    # Save JSON to SQLite
                    database.save_analysis(title, doc_analysis)
                    
                    try:
                        connected_titles = list(set([
                            c["relates_to"] for c in doc_connections
                        ]))
                        if connected_titles:
                            # Let's update Pinecone vector metadata for all chunks of this title!
                            asyncio.create_task(update_pinecone_connections(title, connected_titles))
                    except Exception as pc_err:
                        logger.error(f"Failed to queue Pinecone metadata update for {title}: {pc_err}")

            # Update connections bi-directionally for any referenced documents that were NOT in the current batch
            batch_titles_set = {d.get("title") for d in batch_docs if d.get("title")}
            for c in normalized_connections:
                doc_a = c["doc_id"]
                doc_b = c["relates_to"]
                conn_desc = c["connection"]
                
                # Check both source-target directions
                for source_doc, target_doc in [(doc_a, doc_b), (doc_b, doc_a)]:
                    if source_doc not in batch_titles_set:
                        try:
                            source_analysis = database.get_analysis(source_doc)
                            if source_analysis:
                                existing_conns = source_analysis.get("suggested_connections", [])
                                exists = any(
                                    str(conn.get("relates_to")).lower() == target_doc.lower()
                                    for conn in existing_conns
                                )
                                if not exists:
                                    logger.info(f"Adding bi-directional connection on existing doc {source_doc} -> {target_doc}")
                                    existing_conns.append({
                                        "relates_to": target_doc,
                                        "connection": conn_desc
                                    })
                                    source_analysis["suggested_connections"] = existing_conns
                                    source_analysis["last_updated_by_connection"] = datetime.now().isoformat()
                                    database.save_analysis(source_doc, source_analysis)
                                    
                                    # Also update Pinecone metadata for this existing document to add the new connection
                                    connected_titles = list(set([
                                        conn["relates_to"] for conn in existing_conns
                                    ]))
                                    asyncio.create_task(update_pinecone_connections(source_doc, connected_titles))
                        except Exception as upd_err:
                            logger.error(f"Failed to update bi-directional connection on existing doc {source_doc}: {upd_err}")
            
            # Update progress
            ANALYSIS_STATUS["processed_documents"] += len(batch_docs)
            ANALYSIS_STATUS["last_updated"] = datetime.now().isoformat()
            
            # Sleep briefly to yield execution and prevent rate limit issues
            await asyncio.sleep(0.5)
            
        # Record spending
        spending_tracker.record_analysis({
            "analysis_type": analysis_type,
            "document_count": len(documents),
            "total_cost": estimate.get("total_cost", 0),
            "input_tokens": estimate.get("total_input_tokens", 0),
            "output_tokens": estimate.get("total_output_tokens", 0)
        })
        
        if ANALYSIS_STATUS["status"] == "running":
            ANALYSIS_STATUS["status"] = "completed"
        
        ANALYSIS_STATUS["last_updated"] = datetime.now().isoformat()
        logger.info(f"✅ Background Analysis Complete! Processed {len(unique_titles)} documents.")
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"❌ Background Analysis failed: {error_msg}")
        ANALYSIS_STATUS["status"] = "error"
        ANALYSIS_STATUS["error"] = error_msg
        ANALYSIS_STATUS["last_updated"] = datetime.now().isoformat()


@app.post("/analyze-documents")
async def analyze_documents(request: AnalyzeRequest, background_tasks: BackgroundTasks):
    """
    Run Claude second-pass analysis on documents in background batches with budget enforcement.
    """
    try:
        # Check if already running to prevent concurrent loops
        if ANALYSIS_STATUS["status"] == "running":
            raise HTTPException(status_code=400, detail="An analysis task is already running.")

        analysis_type = request.analysis_type or "recent"
        limit = request.limit or 50
        filters = request.filters
        selected_titles = request.selected_titles or []

        # Retrieve documents from Pinecone
        query_vector = [0.1] * PINECONE_DIMENSION
        matches = []

        if analysis_type == "recent":
            results = await pinecone_with_retry(
                lambda: index.query(
                    vector=query_vector,
                    top_k=min(limit, 500),
                    include_metadata=True
                ),
                max_retries=2,
                timeout=30.0
            )
            matches = results.matches
        elif analysis_type == "full":
            results = await pinecone_with_retry(
                lambda: index.query(
                    vector=query_vector,
                    top_k=1000,
                    include_metadata=True
                ),
                max_retries=2,
                timeout=30.0
            )
            matches = results.matches
        elif analysis_type == "pending":
            all_docs = database.get_all_documents()
            pending_titles = [d['title'] for d in all_docs if d.get('status') != 'analyzed' and not d.get('analysis_results')]
            titles_to_process = pending_titles[:limit]
            logger.info(f"Found {len(pending_titles)} pending documents. Fetching top {len(titles_to_process)} from Pinecone.")
            
            for title in titles_to_process:
                try:
                    results = await pinecone_with_retry(
                        lambda: index.query(
                            vector=query_vector,
                            top_k=500,
                            filter={"title": title},
                            include_metadata=True
                        ),
                        max_retries=2,
                        timeout=30.0
                    )
                    if results and results.matches:
                        matches.extend(results.matches)
                except Exception as e:
                    logger.error(f"Failed to fetch pending document '{title}' from Pinecone: {e}")
        elif analysis_type == "theme":
            results = await pinecone_with_retry(
                lambda: index.query(
                    vector=query_vector,
                    top_k=500,
                    include_metadata=True,
                    filter=filters or {}
                ),
                max_retries=2,
                timeout=30.0
            )
            matches = results.matches
        elif analysis_type == "selected":
            if not selected_titles:
                raise HTTPException(status_code=400, detail="No documents selected for analysis")
            
            logger.info(f"Retrieving {len(selected_titles)} selected documents for Claude analysis")
            
            for title in selected_titles:
                results = await pinecone_with_retry(
                    lambda: index.query(
                        vector=query_vector,
                        top_k=min(limit, 500),
                        include_metadata=True,
                        filter={"title": title}
                    ),
                    max_retries=2,
                    timeout=15.0
                )
                matches.extend(results.matches)
        else:
            raise HTTPException(status_code=400, detail="Invalid analysis_type")

        # AGGREGATION LOGIC
        unique_matches_map = {}
        for match in matches:
            if match and hasattr(match, "metadata") and match.metadata:
                title = match.metadata.get("title", "Unknown")
                if title == "Unknown":
                    continue
                    
                if title not in unique_matches_map:
                    unique_matches_map[title] = {
                        "id": title, 
                        "text_chunks": [], 
                        "tags": set(match.metadata.get("tags", [])), 
                        "title": title
                    }
                
                chunk_text = match.metadata.get("text", "")
                chunk_idx = match.metadata.get("chunk_index", 0)
                unique_matches_map[title]["text_chunks"].append((chunk_idx, chunk_text))
                
                existing_tags = unique_matches_map[title]["tags"]
                new_tags = match.metadata.get("tags", [])
                existing_tags.update(new_tags)
        
        # Reconstruct full text
        documents = []
        for doc_data in unique_matches_map.values():
            sorted_chunks = sorted(doc_data["text_chunks"], key=lambda x: x[0])
            full_text = "\n".join([c[1] for c in sorted_chunks])
            
            doc_data["text"] = full_text
            doc_data["tags"] = list(doc_data["tags"])
            del doc_data["text_chunks"]
            
            documents.append(doc_data)
            
        logger.info(f"Aggregated {len(documents)} unique documents for analysis")

        if not documents:
            return {
                "status": "success",
                "message": "No documents found to analyze",
                "documents_found": 0
            }

        # Estimate cost
        mock_matches_for_est = [{"metadata": {"text": d["text"], "tags": d["tags"]}} for d in documents]
        estimate = estimate_claude_cost(mock_matches_for_est, batch_size=5)

        budget_ok = spending_tracker.can_afford(estimate.get("total_cost", 0))
        if not budget_ok.get("can_afford", True):
            return {
                "status": "budget_exceeded",
                "estimate": estimate,
                "budget": budget_ok
            }

        # Queue background task
        background_tasks.add_task(
            run_analysis_task, 
            documents=documents, 
            analysis_type=analysis_type, 
            estimate=estimate
        )

        return {
            "status": "success",
            "message": f"Claude deep analysis for {len(documents)} documents started in background.",
            "documents_analyzed": len(documents),
            "estimate": estimate
        }

    except HTTPException:
        raise
    except asyncio.TimeoutError:
        logger.error("Analysis timed out waiting for Pinecone")
        raise HTTPException(status_code=504, detail="Analysis timed out - please try again")
    except Exception as e:
        logger.error(f"Analyze documents failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/analysis-status")
async def get_analysis_status():
    """Get status of the background analysis task"""
    return ANALYSIS_STATUS


@app.get("/document-analysis/{title}")
async def get_document_analysis(title: str):
    """Retrieve saved deep analysis results for a document"""
    try:
        analysis = database.get_analysis(title)
        if not analysis:
            raise HTTPException(status_code=404, detail=f"Analysis not found for document: {title}")
        return {
            "status": "success",
            "title": title,
            "analysis": analysis
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
