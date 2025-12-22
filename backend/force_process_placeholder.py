
import asyncio
import os
import sqlite3
from tagging import claude_second_pass_analysis
from database import Database
from main import app  # To access clients if needed, or just import tagging directly

# Initialize DB
database = Database()

async def force_process_pending():
    print("🚀 Starting manual force-processing of pending documents...")
    
    # 1. Get all documents that need analysis
    with sqlite3.connect(database.db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT title FROM documents WHERE status IN ('tagged')")
        titles = [r[0] for r in cursor.fetchall()]

    if not titles:
        print("✅ No pending documents found! All done.")
        return

    print(f"📋 Found {len(titles)} pending documents.")
    
    # 2. Process in batches of 10 to be safe
    BATCH_SIZE = 10
    
    # Need to fetch vector data to run analysis (mimicking main.py logic)
    # This is complex to replicate entirely in a script. 
    # EASIER WAY: Call the internal logic of the backend directly?
    
    # Actually, simpler: Reset the status of 'processing' ones to 'tagged' first to be clean.
    with sqlite3.connect(database.db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE documents SET status='tagged' WHERE status='processing'")
        conn.commit()
        
    print("🔄 Reset any stuck 'processing' docs to 'tagged'.")
    
    # We will use the existing functionality in a way that bypasses UI.
    # But since the analysis requires Pinecone data, running it as a script is tricky without all the async setup.
    
    print("⚠️ To properly run this, we should use the API actually.")
    print("I will use python requests to hit the local API endpoint directly 56 times.")

if __name__ == "__main__":
    # We won't run the complex script. We'll utilize the simpler approach below.
    pass
