
import sqlite3
import os

DB_PATH = "backend/consciousness.db"

def inspect_docs():
    print(f"--- Inspecting Document Versions in {DB_PATH} ---")
    if not os.path.exists(DB_PATH):
        print("❌ Database file not found!")
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Check columns
        cursor.execute("PRAGMA table_info(documents)")
        columns = [r['name'] for r in cursor.fetchall()]
        print(f"Columns: {columns}")

        # Get all documents
        cursor.execute("SELECT title, chunk_count, status, created_at, last_updated FROM documents")
        rows = cursor.fetchall()
        
        print(f"\nFound {len(rows)} documents:")
        v2_count = 0
        v1_count = 0
        
        for r in rows:
            # Heuristic: V2 docs usually have fewer chunks (1800 chars vs 300 chars)
            # Typically a normal book/paper might be 50-200 chunks in V2, vs 300-1200 in V1.
            # But we can also check if we added a specific column or just infer.
            if 'schema_version' in columns:
                ver = r['schema_version'] # If column exists
            else:
                ver = "?"
            
            print(f"  - [{r['status']}] {r['title'][:40]}... | Chunks: {r['chunk_count']} | Last Upd: {r['last_updated']}")

    except Exception as e:
        print(f"❌ SQLite Error: {e}")
    finally:
        if conn: conn.close()

if __name__ == "__main__":
    inspect_docs()
