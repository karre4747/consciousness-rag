"""
Evolve Consciousness Engine - Database Module
SQLite database for analysis tracking, connection storage, and training data generation
Updated: December 22, 2025
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "consciousness.db")


def init_db():
    """Initialize the database with required tables"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Documents table - track uploaded documents
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT UNIQUE NOT NULL,
            source TEXT,
            chunk_count INTEGER,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            analyzed_at TIMESTAMP,
            analysis_status TEXT DEFAULT 'pending'
        )
    """)
    
    # Document analysis table - store Claude's individual analysis
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS document_analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id INTEGER NOT NULL,
            themes TEXT,
            consciousness_patterns TEXT,
            key_concepts TEXT,
            consciousness_level TEXT,
            cross_tradition_links TEXT,
            analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (document_id) REFERENCES documents(id)
        )
    """)
    
    # Connections table - store cross-document connections
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS connections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            doc1_id INTEGER NOT NULL,
            doc2_id INTEGER NOT NULL,
            connection_type TEXT,
            connection_description TEXT,
            strength REAL,
            discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (doc1_id) REFERENCES documents(id),
            FOREIGN KEY (doc2_id) REFERENCES documents(id)
        )
    """)
    
    # Analysis jobs table - track analysis progress
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analysis_jobs (
            id TEXT PRIMARY KEY,
            status TEXT DEFAULT 'running',
            level INTEGER,
            total_documents INTEGER,
            processed_documents INTEGER DEFAULT 0,
            current_document TEXT,
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP,
            error_message TEXT
        )
    """)
    
    # Training data table - store generated training pairs
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS training_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prompt TEXT NOT NULL,
            completion TEXT NOT NULL,
            source_doc1 TEXT,
            source_doc2 TEXT,
            quality_score REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            exported BOOLEAN DEFAULT 0
        )
    """)
    
    conn.commit()
    conn.close()


# ============================================================================
# DOCUMENT OPERATIONS
# ============================================================================

def add_document(title: str, source: str, chunk_count: int) -> int:
    """Add a new document to the database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO documents (title, source, chunk_count)
            VALUES (?, ?, ?)
        """, (title, source, chunk_count))
        doc_id = cursor.lastrowid
        conn.commit()
        return doc_id
    except sqlite3.IntegrityError:
        # Document already exists, update it
        cursor.execute("""
            UPDATE documents 
            SET source = ?, chunk_count = ?, uploaded_at = CURRENT_TIMESTAMP
            WHERE title = ?
        """, (source, chunk_count, title))
        conn.commit()
        cursor.execute("SELECT id FROM documents WHERE title = ?", (title,))
        return cursor.fetchone()[0]
    finally:
        conn.close()


def get_document_by_title(title: str) -> Optional[Dict[str, Any]]:
    """Get document by title"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, title, source, chunk_count, uploaded_at, analyzed_at, analysis_status
        FROM documents
        WHERE title = ?
    """, (title,))
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            'id': row[0],
            'title': row[1],
            'source': row[2],
            'chunk_count': row[3],
            'uploaded_at': row[4],
            'analyzed_at': row[5],
            'analysis_status': row[6]
        }
    return None


def get_all_documents() -> List[Dict[str, Any]]:
    """Get all documents"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, title, source, chunk_count, uploaded_at, analyzed_at, analysis_status
        FROM documents
        ORDER BY uploaded_at DESC
    """)
    
    documents = []
    for row in cursor.fetchall():
        documents.append({
            'id': row[0],
            'title': row[1],
            'source': row[2],
            'chunk_count': row[3],
            'uploaded_at': row[4],
            'analyzed_at': row[5],
            'analysis_status': row[6]
        })
    
    conn.close()
    return documents


def get_unanalyzed_documents() -> List[Dict[str, Any]]:
    """Get documents that haven't been analyzed yet"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, title, source, chunk_count
        FROM documents
        WHERE analysis_status = 'pending'
        ORDER BY uploaded_at ASC
    """)
    
    documents = []
    for row in cursor.fetchall():
        documents.append({
            'id': row[0],
            'title': row[1],
            'source': row[2],
            'chunk_count': row[3]
        })
    
    conn.close()
    return documents


def delete_document(title: str):
    """Delete a document and its analysis"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get document ID
    cursor.execute("SELECT id FROM documents WHERE title = ?", (title,))
    row = cursor.fetchone()
    
    if row:
        doc_id = row[0]
        
        # Delete related records
        cursor.execute("DELETE FROM document_analysis WHERE document_id = ?", (doc_id,))
        cursor.execute("DELETE FROM connections WHERE doc1_id = ? OR doc2_id = ?", (doc_id, doc_id))
        cursor.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
        
        conn.commit()
    
    conn.close()


# ============================================================================
# ANALYSIS OPERATIONS
# ============================================================================

def save_document_analysis(document_id: int, analysis: Dict[str, Any]):
    """Save Claude's analysis of a document"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO document_analysis 
        (document_id, themes, consciousness_patterns, key_concepts, 
         consciousness_level, cross_tradition_links)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        document_id,
        json.dumps(analysis.get('themes', [])),
        json.dumps(analysis.get('consciousness_patterns', [])),
        json.dumps(analysis.get('key_concepts', [])),
        analysis.get('consciousness_level', ''),
        json.dumps(analysis.get('cross_tradition_links', []))
    ))
    
    # Update document status
    cursor.execute("""
        UPDATE documents 
        SET analyzed_at = CURRENT_TIMESTAMP, analysis_status = 'completed'
        WHERE id = ?
    """, (document_id,))
    
    conn.commit()
    conn.close()


def get_document_analysis(document_id: int) -> Optional[Dict[str, Any]]:
    """Get analysis for a document"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT themes, consciousness_patterns, key_concepts, 
               consciousness_level, cross_tradition_links, analyzed_at
        FROM document_analysis
        WHERE document_id = ?
        ORDER BY analyzed_at DESC
        LIMIT 1
    """, (document_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            'themes': json.loads(row[0]) if row[0] else [],
            'consciousness_patterns': json.loads(row[1]) if row[1] else [],
            'key_concepts': json.loads(row[2]) if row[2] else [],
            'consciousness_level': row[3],
            'cross_tradition_links': json.loads(row[4]) if row[4] else [],
            'analyzed_at': row[5]
        }
    return None


# ============================================================================
# CONNECTION OPERATIONS
# ============================================================================

def save_connection(doc1_id: int, doc2_id: int, connection_type: str, 
                   description: str, strength: float = 0.5):
    """Save a cross-document connection"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO connections 
        (doc1_id, doc2_id, connection_type, connection_description, strength)
        VALUES (?, ?, ?, ?, ?)
    """, (doc1_id, doc2_id, connection_type, description, strength))
    
    conn.commit()
    conn.close()


def get_connections_for_document(document_id: int) -> List[Dict[str, Any]]:
    """Get all connections for a document"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT c.id, d1.title as doc1_title, d2.title as doc2_title,
               c.connection_type, c.connection_description, c.strength, c.discovered_at
        FROM connections c
        JOIN documents d1 ON c.doc1_id = d1.id
        JOIN documents d2 ON c.doc2_id = d2.id
        WHERE c.doc1_id = ? OR c.doc2_id = ?
        ORDER BY c.strength DESC
    """, (document_id, document_id))
    
    connections = []
    for row in cursor.fetchall():
        connections.append({
            'id': row[0],
            'doc1_title': row[1],
            'doc2_title': row[2],
            'connection_type': row[3],
            'description': row[4],
            'strength': row[5],
            'discovered_at': row[6]
        })
    
    conn.close()
    return connections


def get_all_connections() -> List[Dict[str, Any]]:
    """Get all connections"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT c.id, d1.title as doc1_title, d2.title as doc2_title,
               c.connection_type, c.connection_description, c.strength, c.discovered_at
        FROM connections c
        JOIN documents d1 ON c.doc1_id = d1.id
        JOIN documents d2 ON c.doc2_id = d2.id
        ORDER BY c.strength DESC
    """)
    
    connections = []
    for row in cursor.fetchall():
        connections.append({
            'id': row[0],
            'doc1_title': row[1],
            'doc2_title': row[2],
            'connection_type': row[3],
            'description': row[4],
            'strength': row[5],
            'discovered_at': row[6]
        })
    
    conn.close()
    return connections


# ============================================================================
# ANALYSIS JOB OPERATIONS
# ============================================================================

def create_analysis_job(job_id: str, level: int, total_documents: int) -> str:
    """Create a new analysis job"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO analysis_jobs (id, level, total_documents)
        VALUES (?, ?, ?)
    """, (job_id, level, total_documents))
    
    conn.commit()
    conn.close()
    return job_id


def update_analysis_job_progress(job_id: str, processed: int, current_doc: str):
    """Update analysis job progress"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE analysis_jobs
        SET processed_documents = ?, current_document = ?
        WHERE id = ?
    """, (processed, current_doc, job_id))
    
    conn.commit()
    conn.close()


def complete_analysis_job(job_id: str, error: Optional[str] = None):
    """Mark analysis job as complete"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    if error:
        cursor.execute("""
            UPDATE analysis_jobs
            SET status = 'failed', completed_at = CURRENT_TIMESTAMP, error_message = ?
            WHERE id = ?
        """, (error, job_id))
    else:
        cursor.execute("""
            UPDATE analysis_jobs
            SET status = 'completed', completed_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (job_id,))
    
    conn.commit()
    conn.close()


def get_analysis_job(job_id: str) -> Optional[Dict[str, Any]]:
    """Get analysis job status"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, status, level, total_documents, processed_documents, 
               current_document, started_at, completed_at, error_message
        FROM analysis_jobs
        WHERE id = ?
    """, (job_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            'id': row[0],
            'status': row[1],
            'level': row[2],
            'total_documents': row[3],
            'processed_documents': row[4],
            'current_document': row[5],
            'started_at': row[6],
            'completed_at': row[7],
            'error_message': row[8]
        }
    return None


# ============================================================================
# TRAINING DATA OPERATIONS
# ============================================================================

def save_training_pair(prompt: str, completion: str, source_doc1: str = None, 
                       source_doc2: str = None, quality_score: float = 1.0):
    """Save a training data pair"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO training_data 
        (prompt, completion, source_doc1, source_doc2, quality_score)
        VALUES (?, ?, ?, ?, ?)
    """, (prompt, completion, source_doc1, source_doc2, quality_score))
    
    conn.commit()
    conn.close()


def get_training_data(exported_only: bool = False) -> List[Dict[str, Any]]:
    """Get training data pairs"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    if exported_only:
        cursor.execute("""
            SELECT id, prompt, completion, source_doc1, source_doc2, quality_score, created_at
            FROM training_data
            WHERE exported = 0
            ORDER BY quality_score DESC, created_at DESC
        """)
    else:
        cursor.execute("""
            SELECT id, prompt, completion, source_doc1, source_doc2, quality_score, created_at
            FROM training_data
            ORDER BY quality_score DESC, created_at DESC
        """)
    
    training_pairs = []
    for row in cursor.fetchall():
        training_pairs.append({
            'id': row[0],
            'prompt': row[1],
            'completion': row[2],
            'source_doc1': row[3],
            'source_doc2': row[4],
            'quality_score': row[5],
            'created_at': row[6]
        })
    
    conn.close()
    return training_pairs


def mark_training_data_exported(ids: List[int]):
    """Mark training data as exported"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    placeholders = ','.join('?' * len(ids))
    cursor.execute(f"""
        UPDATE training_data
        SET exported = 1
        WHERE id IN ({placeholders})
    """, ids)
    
    conn.commit()
    conn.close()


# ============================================================================
# STATISTICS
# ============================================================================

def get_stats() -> Dict[str, Any]:
    """Get database statistics"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM documents")
    total_docs = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM documents WHERE analysis_status = 'completed'")
    analyzed_docs = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM connections")
    total_connections = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM training_data")
    total_training_pairs = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM training_data WHERE exported = 0")
    unexported_training_pairs = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        'total_documents': total_docs,
        'analyzed_documents': analyzed_docs,
        'pending_analysis': total_docs - analyzed_docs,
        'total_connections': total_connections,
        'total_training_pairs': total_training_pairs,
        'unexported_training_pairs': unexported_training_pairs
    }


# Initialize database on import
init_db()
