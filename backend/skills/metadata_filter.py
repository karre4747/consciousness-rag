import os
import glob
import logging
import sqlite3
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

# Base path for local library folder
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIBRARY_DIR = os.path.join(BASE_DIR, "library")
DB_PATH = os.path.join(BASE_DIR, "consciousness.db")

# Mapping of collection names to subfolders
COLLECTION_FOLDERS = {
    "addiction_recovery": "addiction_recovery",
    "metaphysics": "metaphysics",
    "science_bridge": "science_bridge",
    "healing_modalities": "healing_modalities"
}

def get_collection_documents(collection_name: str) -> List[str]:
    """
    Get all document titles belonging to a given collection.
    Scans the local library folder structure if available,
    otherwise falls back to rule-based tag detection in the SQLite database.
    """
    titles = []
    
    # 1. Try local folder structure scan (most accurate)
    subfolder = COLLECTION_FOLDERS.get(collection_name)
    if subfolder:
        target_path = os.path.join(LIBRARY_DIR, subfolder)
        if os.path.exists(target_path):
            # Find all files recursively (PDF, DOCX)
            for file_path in glob.glob(os.path.join(target_path, "**/*.*"), recursive=True):
                if file_path.lower().endswith(('.pdf', '.docx')):
                    titles.append(os.path.basename(file_path))
                    
    # 2. Fall back to rule-based tag/title detection from SQLite
    if not titles and os.path.exists(DB_PATH):
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Fetch all documents to classify them dynamically
            cursor.execute("SELECT title, status FROM documents")
            db_docs = cursor.fetchall()
            
            for doc in db_docs:
                title = doc["title"]
                title_lower = title.lower()
                
                # Rule-based classification mapping
                matched_collection = None
                
                if collection_name == "addiction_recovery":
                    if any(w in title_lower for w in ["step", "sober", "aa-", "na-", "big-book", "recovery", "addiction", "substance", "boundaries"]):
                        matched_collection = "addiction_recovery"
                elif collection_name == "metaphysics":
                    if any(w in title_lower for w in ["kybalion", "mysticism", "theosophy", "blavatsky", "secret-doctrine", "goddard", "murphy", "subconscious", "astrology", "wisdom", "hermetica", "tesla", "thoth", "pineal"]):
                        matched_collection = "metaphysics"
                elif collection_name == "science_bridge":
                    if any(w in title_lower for w in ["quantum", "physics", "neuro", "brain", "epigenetics", "biology", "biophoton"]):
                        matched_collection = "science_bridge"
                elif collection_name == "healing_modalities":
                    if any(w in title_lower for w in ["dbt", "cbt", "therapy", "somatic", "trauma", "attachment", "inner-child", "breathwork"]):
                        matched_collection = "healing_modalities"
                        
                if matched_collection == collection_name:
                    titles.append(title)
            
            conn.close()
        except Exception as e:
            logger.error(f"Error classifying documents from SQLite: {e}")
            
    # Remove duplicates and return
    return list(set(titles))

def get_pinecone_filter(collection_name: str) -> Dict[str, Any]:
    """
    Generate Pinecone metadata filter query for a specific collection.
    Returns: Dict containing the Pinecone $in title filter, or an empty filter if collection is unknown.
    """
    if collection_name == "synthesis":
        return {} # No filter for synthesis agent (it queries across all collections)
        
    titles = get_collection_documents(collection_name)
    if not titles:
        logger.warning(f"No documents found for collection '{collection_name}'. Returning empty filter.")
        # Return a filter that won't match anything to be safe
        return {"title": "non_existent_doc_placeholder"}
        
    return {"title": {"$in": titles}}
