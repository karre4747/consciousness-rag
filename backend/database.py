import sqlite3
import logging
from datetime import datetime
import os

DB_PATH = "consciousness.db"
logger = logging.getLogger(__name__)

def init_db():
    """Initialize the SQLite database with the documents table"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Create Documents Table
        # Statuses: 'uploaded', 'tagged', 'analyzed'
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS documents (
            title TEXT PRIMARY KEY,
            chunk_count INTEGER DEFAULT 0,
            status TEXT DEFAULT 'uploaded',
            has_keyword_tags BOOLEAN DEFAULT 0,
            ai_provider TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")

def add_document(title, chunk_count, has_keyword_tags=False):
    """Add or update a document"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO documents (title, chunk_count, status, has_keyword_tags, last_updated)
        VALUES (?, ?, 'uploaded', ?, CURRENT_TIMESTAMP)
        ON CONFLICT(title) DO UPDATE SET
            chunk_count = excluded.chunk_count,
            last_updated = CURRENT_TIMESTAMP
        ''', (title, chunk_count, has_keyword_tags))
        
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Failed to add document {title}: {e}")

def update_status(title, status, ai_provider=None):
    """Update document status"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        updates = ["status = ?", "last_updated = CURRENT_TIMESTAMP"]
        params = [status, title]
        
        if ai_provider:
            updates.insert(0, "ai_provider = ?")
            params.insert(0, ai_provider)
            
        # Re-order params: val, [val], title
        query = f"UPDATE documents SET {', '.join(updates)} WHERE title = ?"
        
        # Fix param order for the query
        # If ai_provider: [ai_provider, status, title]
        # Else: [status, title]
        sql_params = [ai_provider, status, title] if ai_provider else [status, title]

        cursor.execute(query, sql_params)
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Failed to update status for {title}: {e}")

def get_documents(status_filter=None):
    """Get documents, optionally filtered by status"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if status_filter:
            cursor.execute("SELECT * FROM documents WHERE status = ? ORDER BY last_updated DESC", (status_filter,))
        else:
            cursor.execute("SELECT * FROM documents ORDER BY title")
            
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Failed to get documents: {e}")
        return []

def get_stats():
    """Get simple counts"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM documents")
        total = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM documents WHERE status='uploaded'")
        pending_tag = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM documents WHERE status='tagged'")
        pending_analyze = cursor.fetchone()[0]
        
        conn.close()
        return {"total": total, "pending_tag": pending_tag, "pending_analyze": pending_analyze}
    except Exception as e:
        return {"total": 0, "pending_tag": 0, "pending_analyze": 0}
