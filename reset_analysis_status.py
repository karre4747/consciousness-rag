
import sqlite3
import os

DB_PATH = "backend/consciousness.db"

def reset_analyzed_documents():
    print(f"--- Resetting Analysis Status in {DB_PATH}) ---")
    if not os.path.exists(DB_PATH):
        print("❌ Database file not found!")
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Count analyzed docs
        cursor.execute("SELECT COUNT(*) FROM documents WHERE status = 'analyzed'")
        count = cursor.fetchone()[0]
        print(f"Found {count} documents marked as 'analyzed'.")

        if count > 0:
            print("Resetting status to 'tagged'...")
            cursor.execute("UPDATE documents SET status = 'tagged' WHERE status = 'analyzed'")
            conn.commit()
            print(f"✅ Successfully reset {count} documents. They should now appear in the Analysis tab.")
        else:
            print("No documents found to reset.")

    except Exception as e:
        print(f"❌ SQLite Error: {e}")
    finally:
        if conn: conn.close()

if __name__ == "__main__":
    reset_analyzed_documents()
