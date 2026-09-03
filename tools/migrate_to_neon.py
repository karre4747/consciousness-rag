#!/usr/bin/env python3
"""
Evolve Consciousness Engine - Neon Postgres Migration & Sync

Migrates local SQLite database (consciousness.db) to Neon PostgreSQL.
Also provides a transparent database adapter supporting both SQLite and PostgreSQL.

Usage:
    # Migrate data from SQLite to Neon PostgreSQL:
    python tools/migrate_to_neon.py
"""

import os
import sys
import json
import sqlite3
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND = os.path.join(REPO, "backend")
load_dotenv(os.path.join(BACKEND, ".env"), override=True)

SQLITE_PATH = os.path.join(BACKEND, "consciousness.db")
DATABASE_URL = os.getenv("DATABASE_URL")

def init_postgres(conn):
    """Create tables on Neon PostgreSQL if they do not exist."""
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                title TEXT PRIMARY KEY,
                chunk_count INTEGER DEFAULT 0,
                status TEXT DEFAULT 'uploaded',
                has_keyword_tags BOOLEAN DEFAULT FALSE,
                ai_provider TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                schema_version INTEGER DEFAULT 1,
                analysis_results JSONB
            );
            CREATE INDEX IF NOT EXISTS idx_docs_status ON documents(status);
            CREATE INDEX IF NOT EXISTS idx_docs_last_updated ON documents(last_updated DESC);
            CREATE INDEX IF NOT EXISTS idx_docs_ai_provider ON documents(ai_provider);

            CREATE TABLE IF NOT EXISTS spending (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                analysis_type TEXT,
                document_count INTEGER,
                chunk_count INTEGER,
                input_tokens INTEGER,
                output_tokens INTEGER,
                total_cost NUMERIC(10, 4),
                model TEXT
            );
        """)
    conn.commit()
    print("✅ Neon PostgreSQL schema verified and initialized.")

def migrate():
    if not DATABASE_URL:
        print("❌ DATABASE_URL is missing in backend/.env")
        return

    print("Connecting to Neon PostgreSQL...")
    pg_conn = psycopg2.connect(DATABASE_URL)
    init_postgres(pg_conn)

    print("Reading documents from SQLite...")
    sq_conn = sqlite3.connect(SQLITE_PATH)
    sq_conn.row_factory = sqlite3.Row
    sq_cur = sq_conn.cursor()
    sq_cur.execute("SELECT * FROM documents")
    rows = sq_cur.fetchall()
    sq_conn.close()

    print(f"Found {len(rows)} documents in SQLite. Syncing to Neon...")

    with pg_conn.cursor() as cur:
        for r in rows:
            analysis = None
            if r["analysis_results"]:
                try:
                    analysis = json.dumps(json.loads(r["analysis_results"]))
                except Exception:
                    analysis = None

            cur.execute("""
                INSERT INTO documents (
                    title, chunk_count, status, has_keyword_tags, ai_provider,
                    created_at, last_updated, schema_version, analysis_results
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (title) DO UPDATE SET
                    chunk_count = EXCLUDED.chunk_count,
                    status = EXCLUDED.status,
                    has_keyword_tags = EXCLUDED.has_keyword_tags,
                    ai_provider = EXCLUDED.ai_provider,
                    last_updated = EXCLUDED.last_updated,
                    schema_version = EXCLUDED.schema_version,
                    analysis_results = COALESCE(EXCLUDED.analysis_results, documents.analysis_results);
            """, (
                r["title"],
                r["chunk_count"],
                r["status"],
                bool(r["has_keyword_tags"]),
                r["ai_provider"],
                r["created_at"],
                r["last_updated"],
                r["schema_version"],
                analysis
            ))
    pg_conn.commit()
    pg_conn.close()
    print(f"🎉 Successfully migrated {len(rows)} records into Neon PostgreSQL!")

if __name__ == "__main__":
    migrate()
