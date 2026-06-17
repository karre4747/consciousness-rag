import os
import logging
from typing import List, Dict, Any
from dotenv import load_dotenv
from pinecone import Pinecone
from openai import OpenAI

logger = logging.getLogger(__name__)

# Load backend dotenv configuration
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(BASE_DIR, ".env")
load_dotenv(ENV_PATH, override=True)

# Initialize API clients
pinecone_key = os.getenv("PINECONE_API_KEY")
openai_key = os.getenv("OPENAI_API_KEY")

if not pinecone_key or not openai_key:
    logger.error("Missing PINECONE_API_KEY or OPENAI_API_KEY in skills/semantic_search.py")

pc = Pinecone(api_key=pinecone_key)
openai_client = OpenAI(api_key=openai_key)

index_name = os.getenv("PINECONE_INDEX_NAME", "evolve-consciousness-v3")
index = pc.Index(index_name)

embedding_model = os.getenv("EMBEDDING_MODEL", "text-embedding-3-large")

def query_vector_db(query: str, top_k: int = 5, filter_dict: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    """
    Generate embedding for the query, query Pinecone with optional metadata filters,
    and return list of matching documents/chunks.
    """
    try:
        # 1. Generate Query Embedding
        resp = openai_client.embeddings.create(
            model=embedding_model,
            input=query
        )
        query_vector = resp.data[0].embedding
        
        # 2. Query Pinecone
        # Clean up empty filter dicts
        active_filter = filter_dict if filter_dict else None
        
        results = index.query(
            vector=query_vector,
            top_k=top_k,
            filter=active_filter,
            include_metadata=True
        )
        
        # 3. Format Matches
        formatted_matches = []
        for match in results.matches:
            metadata = match.metadata if match.metadata else {}
            formatted_matches.append({
                "id": match.id,
                "score": match.score,
                "text": metadata.get("text", ""),
                "title": metadata.get("title", "unknown"),
                "chunk_index": metadata.get("chunk_index", 0),
                "tags": metadata.get("tags", []),
                "metadata": metadata
            })
            
        logger.info(f"Query '{query[:30]}...' returned {len(formatted_matches)} vectors from index '{index_name}'")
        return formatted_matches
        
    except Exception as e:
        logger.error(f"Semantic search failed: {e}")
        return []
