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

        # PERFORMANCE FIX: Add indexes for frequently queried columns
        # These indexes dramatically improve filtering and sorting performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_status ON documents(status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_last_updated ON documents(last_updated DESC)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_ai_provider ON documents(ai_provider)')

        conn.commit()
        conn.close()
        logger.info("Database initialized successfully with performance indexes")

        # Run Migrations immediately after init
        migrate_db_v2()
        migrate_db_v3()

    except Exception as e:
        logger.error(f"Database initialization failed: {e}")

def migrate_db_v2():
    """Add schema_version column if it doesn't exist"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Check if column exists
        cursor.execute("PRAGMA table_info(documents)")
        columns = [info[1] for info in cursor.fetchall()]

        if "schema_version" not in columns:
            logger.info("Migrating database to V2 (Adding schema_version)...")
            cursor.execute("ALTER TABLE documents ADD COLUMN schema_version INTEGER DEFAULT 1")
            conn.commit()
            logger.info("Migration successful: schema_version added")
        else:
            logger.info("Database already at V2 schema")

        conn.close()
    except Exception as e:
        logger.error(f"Migration V2 failed: {e}")

def migrate_db_v3():
    """Add analysis_results column to store Claude deep analysis"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Check if column exists
        cursor.execute("PRAGMA table_info(documents)")
        columns = [info[1] for info in cursor.fetchall()]

        if "analysis_results" not in columns:
            logger.info("Migrating database to V3 (Adding analysis_results for deep analysis storage)...")
            cursor.execute("ALTER TABLE documents ADD COLUMN analysis_results TEXT")
            conn.commit()
            logger.info("Migration successful: analysis_results column added")
        else:
            logger.info("Database already at V3 schema")

        conn.close()
    except Exception as e:
        logger.error(f"Migration V3 failed: {e}")

def add_document(title, chunk_count, has_keyword_tags=False, ai_provider=None):
    """Add or update a document with proper error handling"""
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute('''
        INSERT INTO documents (title, chunk_count, status, has_keyword_tags, ai_provider, last_updated)
        VALUES (?, ?, 'uploaded', ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(title) DO UPDATE SET
            chunk_count = excluded.chunk_count,
            ai_provider = COALESCE(excluded.ai_provider, documents.ai_provider),
            last_updated = CURRENT_TIMESTAMP
        ''', (title, chunk_count, has_keyword_tags, ai_provider))

        conn.commit()
        logger.debug(f"Added/updated document {title} with {chunk_count} chunks")
    except Exception as e:
        logger.error(f"Failed to add document {title}: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()

def update_status(title, status, ai_provider=None, schema_version=None):
    """Update document status with proper error handling and rollback"""
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Build clean SET clause with proper parameter ordering
        set_values = []
        sql_params = []

        if schema_version is not None:
            set_values.append("schema_version = ?")
            sql_params.append(schema_version)

        if ai_provider:
            set_values.append("ai_provider = ?")
            sql_params.append(ai_provider)

        set_values.append("status = ?")
        sql_params.append(status)

        set_values.append("last_updated = CURRENT_TIMESTAMP")

        # Add WHERE param
        sql_params.append(title)

        query = f"UPDATE documents SET {', '.join(set_values)} WHERE title = ?"

        cursor.execute(query, sql_params)
        conn.commit()
        logger.debug(f"Updated status for {title} to {status}")
    except Exception as e:
        logger.error(f"Failed to update status for {title}: {e}")
        if conn:
            conn.rollback()
        raise  # Re-raise to ensure caller knows operation failed
    finally:
        if conn:
            conn.close()

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

def get_document_by_title(title):
    """Get a single document by title"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM documents WHERE title = ?", (title,))
        row = cursor.fetchone()
        conn.close()
        
        return dict(row) if row else None
    except Exception as e:
        logger.error(f"Failed to get document by title {title}: {e}")
        return None

def delete_document(title):
    """Delete a document by title"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM documents WHERE title = ?", (title,))
        conn.commit()
        conn.close()
        logger.info(f"Deleted document from SQLite: {title}")
    except Exception as e:
        logger.error(f"Failed to delete document {title}: {e}")

def save_analysis_results(title, analysis_json):
    """
    Save Claude deep analysis results for a document

    Args:
        title: Document title
        analysis_json: JSON string containing analysis results
    """
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE documents SET analysis_results = ?, last_updated = CURRENT_TIMESTAMP WHERE title = ?",
            (analysis_json, title)
        )

        conn.commit()
        logger.info(f"Saved analysis results for document: {title}")
    except Exception as e:
        logger.error(f"Failed to save analysis results for {title}: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()

def get_analysis_results(title):
    """
    Retrieve stored analysis results for a document

    Args:
        title: Document title

    Returns:
        JSON string of analysis results or None if not found
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("SELECT analysis_results FROM documents WHERE title = ?", (title,))
        row = cursor.fetchone()
        conn.close()

        return row[0] if row else None
    except Exception as e:
        logger.error(f"Failed to retrieve analysis results for {title}: {e}")
        return None
