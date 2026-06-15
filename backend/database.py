"""
Evolve Consciousness Engine - Database Module
SQLite database for analysis tracking, connection storage, and training data generation
Updated: February 2026 (Sync with V2 Architecture)
"""

import sqlite3
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
import os

# Configure logging
logger = logging.getLogger(__name__)

DB_PATH = os.path.join(os.path.dirname(__file__), "consciousness.db")

def get_db_connection():
    """Create a database connection with row factory"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database with required V2 tables"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Documents table - V2 Schema
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            title TEXT PRIMARY KEY,
            chunk_count INTEGER DEFAULT 0,
            status TEXT DEFAULT 'uploaded',
            has_keyword_tags BOOLEAN DEFAULT 0,
            ai_provider TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
            schema_version INTEGER DEFAULT 1,
            analysis_results TEXT
        )
    """)
    
    # Indexes for performance
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_status ON documents(status)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_last_updated ON documents(last_updated DESC)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_ai_provider ON documents(ai_provider)")
    
    # Spending tracking table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS spending (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            analysis_type TEXT,
            document_count INTEGER,
            chunk_count INTEGER,
            input_tokens INTEGER,
            output_tokens INTEGER,
            total_cost REAL,
            ai_provider TEXT
        )
    """)
    
    conn.commit()
    conn.close()

# Use the V2 add_document logic
def add_document(title: str, chunk_count: int, has_tags: bool = False, ai_provider: str = None, schema_version: int = 2) -> bool:
    """Add or update a document in the tracking database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO documents (title, chunk_count, has_keyword_tags, ai_provider, status, last_updated, schema_version)
            VALUES (?, ?, ?, ?, 'uploaded', CURRENT_TIMESTAMP, ?)
            ON CONFLICT(title) DO UPDATE SET
                chunk_count = excluded.chunk_count,
                has_keyword_tags = excluded.has_keyword_tags,
                ai_provider = excluded.ai_provider,
                status = 'uploaded',
                last_updated = CURRENT_TIMESTAMP,
                schema_version = excluded.schema_version
        """, (title, chunk_count, 1 if has_tags else 0, ai_provider, schema_version)) # Default to 2 for new adds
        conn.commit()
        return True
    except Exception as e:
        logger.error(f"Error adding document to SQLite: {e}")
        return False
    finally:
        conn.close()

def update_status(title: str, status: str, ai_provider: str = None, schema_version: int = None):
    """Update document status and optionally AI provider"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        if ai_provider:
            if schema_version:
                cursor.execute("""
                    UPDATE documents 
                    SET status = ?, ai_provider = ?, last_updated = CURRENT_TIMESTAMP, schema_version = ? 
                    WHERE title = ?
                """, (status, ai_provider, schema_version, title))
            else:
                cursor.execute("""
                    UPDATE documents 
                    SET status = ?, ai_provider = ?, last_updated = CURRENT_TIMESTAMP 
                    WHERE title = ?
                """, (status, ai_provider, title))
        else:
            if schema_version:
                cursor.execute("""
                    UPDATE documents 
                    SET status = ?, last_updated = CURRENT_TIMESTAMP, schema_version = ? 
                    WHERE title = ?
                """, (status, schema_version, title))
            else:
                cursor.execute("""
                    UPDATE documents 
                    SET status = ?, last_updated = CURRENT_TIMESTAMP 
                    WHERE title = ?
                """, (status, title))
        conn.commit()
    except Exception as e:
        logger.error(f"Error updating document status: {e}")
    finally:
        conn.close()

def get_all_documents() -> List[Dict[str, Any]]:
    """Get all documents from the database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM documents ORDER BY last_updated DESC")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()

def get_stats() -> Dict[str, Any]:
    """Get high-level stats for the UI"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM documents")
        total = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM documents WHERE status = 'analyzed'")
        analyzed = cursor.fetchone()[0]
        
        cursor.execute("SELECT SUM(chunk_count) FROM documents")
        total_chunks = cursor.fetchone()[0] or 0
        
        return {
            "total_documents": total,
            "analyzed_documents": analyzed,
            "total_chunks": total_chunks
        }
    finally:
        conn.close()

def delete_document(title: str) -> bool:
    """Delete document from SQLite"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM documents WHERE title = ?", (title,))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()

def save_analysis(title: str, results: Dict[str, Any]):
    """Save deep analysis results for a document"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE documents 
            SET status = 'analyzed', analysis_results = ?, last_updated = CURRENT_TIMESTAMP 
            WHERE title = ?
        """, (json.dumps(results), title))
        conn.commit()
    finally:
        conn.close()

def get_analysis(title: str) -> Optional[Dict[str, Any]]:
    """Retrieve deep analysis results for a document"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT analysis_results FROM documents WHERE title = ?", (title,))
        row = cursor.fetchone()
        if row and row[0]:
            return json.loads(row[0])
        return None
    finally:
        conn.close()

# Initialize DB when module loaded
init_db()
