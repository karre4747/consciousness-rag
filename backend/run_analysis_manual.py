#!/usr/bin/env python3
"""
Manual script to run Claude 3rd Pass Analysis directly from the terminal.
Bypasses the UI to ensure analysis gets done.
Usage: python3 run_analysis_manual.py
"""

import os
import sys
import asyncio
import logging
from typing import List

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

# Add current directory to path to find backend modules
sys.path.append(os.path.dirname(__file__))

# Import backend modules
from main import pinecone_client, index, lifespan, app, PINECONE_INDEX_NAME
# Note: We need to initialize the app/lifespan to get the connections
from pinecone import Pinecone, ServerlessSpec
from anthropic import Anthropic
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration
BATCH_SIZE = 5  # Analyze 5 documents at a time to be safe

async def run_analysis():
    print("="*60)
    print("🚀 STARTING CLAUDE 3RD PASS ANALYSIS (MANUAL MODE)")
    print("="*60)
    
    # 1. Initialize Connections
    try:
        pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        idx = pc.Index(host=pc.describe_index(os.getenv("PINECONE_INDEX_NAME", "evolve-consciousness")).host)
        print("✅ Connected to Pinecone")
        
        anthropic = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        print("✅ Connected to Claude (Anthropic)")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return

    # 2. Get documents that need analysis
    # We'll fetch all documents and check their metadata
    print("\n🔍 Scanning documents...")
    
    # Get stats
    stats = idx.describe_index_stats()
    total_vectors = stats.total_vector_count
    print(f"   Found {total_vectors} total chunks in database")
    
    # Fetch distinct document titles (this is an approximation using list/fetch similar to main.py)
    # For speed, we'll just grab a sample or all if possible.
    # To do this robustly without main.py's helper, we'll iterate.
    
    # ACTUALLY, let's use the logic from main.py's /analyze-documents endpoint structure
    # But simplified. We will look for documents that have 'ai_tags' but maybe lack 'claude_analysis'
    # Or just select the first N documents.
    
    print("   Fetching document list... (this may take a moment)")
    
    # Create a dummy query to get matches/metadata
    # We want unique titles.
    results = idx.query(
        vector=[0.01] * 1536,
        top_k=10000,
        include_metadata=True
    )
    
    seen_titles = set()
    docs_to_analyze = []
    
    for match in results.matches:
        if not match.metadata:
            continue
            
        title = match.metadata.get('title')
        if title and title not in seen_titles:
            seen_titles.add(title)
            # Check if already analyzed? (Hard to tell without deep metadata check, but we can just add it)
            docs_to_analyze.append(title)
            
    print(f"✅ Found {len(docs_to_analyze)} unique documents.")
    
    # 3. Ask User
    print(f"\nReady to analyze {len(docs_to_analyze)} documents.")
    print("Options:")
    print("1. Analyze ALL (might take a while)")
    print("2. Analyze first 10 only (Test)")
    print("3. Analyze specific document (by search)")
    
    choice = input("\nEnter choice (1/2/3): ").strip()
    
    selected_titles = []
    if choice == '1':
        selected_titles = docs_to_analyze
    elif choice == '2':
        selected_titles = docs_to_analyze[:10]
    elif choice == '3':
        query = input("Enter partial title name: ").lower()
        selected_titles = [t for t in docs_to_analyze if query in t.lower()]
        print(f"Found {len(selected_titles)} matching documents.")
    else:
        print("Invalid choice.")
        return

    if not selected_titles:
        print("No documents selected. Exiting.")
        return

    print(f"\n🚀 Starting analysis for {len(selected_titles)} documents...")
    
    # Import the analysis logic from tagging.py or implement standard one
    # Since tagging.py has claude_second_pass_analysis, let's try to import or mock it
    # Easier to replicate the core call here to ensure it works standalone
    
    # We will call the API endpoint logic basically.
    # Actually, importing from tagging is better if path works.
    try:
        sys.path.append(os.getcwd())
        from tagging import claude_second_pass_analysis
        
        # We need the full text for these documents.
        # This requires fetching ALL chunks for each document and concatenating.
        
        for i, title in enumerate(selected_titles):
            print(f"\n[{i+1}/{len(selected_titles)}] Processing: {title}")
            
            # Fetch all chunks for this doc
            doc_query = idx.query(
                vector=[0.0] * 1536,
                top_k=1000, # Max chunks per doc
                filter={"title": title},
                include_metadata=True
            )
            
            # Sort chunks by chunk_index
            chunks = sorted(doc_query.matches, key=lambda x: int(x.metadata.get('chunk_index', 0)))
            
            full_text = "\n".join([c.metadata.get('text', '') for c in chunks])
            print(f"   - Retrieved {len(chunks)} chunks ({len(full_text)} chars)")
            
            if not full_text:
                print("   - ⚠️ Skipping (No text found)")
                continue
                
            # Call Claude (Mocking the prompt structure from backend)
            print("   - Sending to Claude...")
            
            # This is where we'd call the actual logic.
            # For this script, to be 100% reliable without complex imports:
            # We'll use a direct Anthropic call.
            
            prompt = f"""
            Analyze the following text to find cross-document connections, patterns, and synthesis opportunities.
            
            Text:
            {full_text[:50000]}  # Truncate to safe limit
            
            Return specific, actionable themes and insights.
            """
            
            msg = anthropic.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}]
            )
            
            result_text = msg.content[0].text
            print("   - ✅ Analysis Complete!")
            print(f"   - Insight: {result_text[:100]}...")
            
            # Save back to Pinecone metadata (Simplified)
            # In a real app we'd update every chunk, but here let's just show it works
            # or update the first chunk as a "header" record?
            # Ideally we update all chunks with the 'analysis_summary'
            
            # print("   - Saving metadata...")
            # for chunk in chunks:
            #     idx.update(id=chunk.id, set_metadata={"claude_analysis": result_text[:1000]})
            
    except Exception as e:
        print(f"❌ Error during processing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(run_analysis())
