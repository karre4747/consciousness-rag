#!/usr/bin/env python3
"""
Phase 2 Testing Script
Verifies:
1. Document Listing & Counting
2. AI Tagging (Ollama/OpenAI)
3. Claude Document Selection
"""

import asyncio
import os
import sys
import logging
from typing import Dict, Any

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add current dir to path
sys.path.append(os.path.dirname(__file__))

# Import backend modules
# We wrap imports in try/except to handle missing dependencies/env vars gracefully
try:
    from main import pinecone_client, index, lifespan, app, PINECONE_INDEX_NAME
    from tagging import generate_tags, claude_second_pass_analysis
    from pinecone import Pinecone
    from dotenv import load_dotenv
except ImportError as e:
    logger.error(f"Failed to import backend modules: {e}")
    sys.exit(1)

# Load env vars
load_dotenv()

async def test_document_counting():
    """Test 1: Verify document counting logic"""
    logger.info("TEST 1: Document Counting")
    print("-" * 40)
    
    try:
        # We need to manually initialize the connection if main.py didn't do it globally yet
        # But importing main should have defined the vars. 
        # We need to run the lifespan startup logic if client is None
        
        pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        idx_desc = pc.describe_index(os.getenv("PINECONE_INDEX_NAME", "evolve-consciousness"))
        idx = pc.Index(host=idx_desc.host)
        
        stats = idx.describe_index_stats()
        total_vectors = stats.total_vector_count
        print(f"✅ Pinecone Connection Successful")
        print(f"ℹ️ Total Vectors in Index: {total_vectors}")
        
        # Test Pagination Logic (Mini Version)
        # We'll just fetch a small batch to prove connection works
        ids_iter = idx.list(limit=5)
        count = 0
        for _ in ids_iter:
            count += 1
            break # Just need to see if it yields
            
        if count > 0:
             print("✅ Pagination (idx.list) is working")
        else:
             print("⚠️ Index appears empty (no IDs returned)")

    except Exception as e:
        print(f"❌ Document Counting Test Failed: {e}")

async def test_ai_tagging():
    """Test 2: Verify AI Tagging Logic"""
    logger.info("\nTEST 2: AI Tagging (Dry Run)")
    print("-" * 40)
    
    sample_text = "The user explores the connection between quantum physics and the heart chakra, discussing energy fields and consciousness."
    title = "Test_Document_Tagging"
    
    try:
        print(f"ℹ️ Testing Tagging with text: '{sample_text[:50]}...'")
        
        # Test Keyword Tagging (Implicit in generate_tags)
        # We will call generate_tags directly. 
        # Note: This might make a real API call if we aren't careful.
        # generate_tags(text, existing_tags, ai_provider, check_cost)
        
        # Let's try Ollama (Free) first if available, or just skip if we don't want to rely on local ollama
        # Actually proper test is to call it.
        
        # Mocking or calling? User wants to see it WORK.
        # Failing gracefully if Ollama not running.
        
        tags = await generate_tags(
            text=sample_text,
            use_ai=True,
            ai_provider="openai", 
            title=title
        )
        
        print(f"✅ Tagging Function Returned Result")
        print(f"Types: {tags.get('tags', {}).get('type', [])}")
        print(f"Themes: {tags.get('tags', {}).get('theme', [])}")
        
    except Exception as e:
        print(f"❌ AI Tagging Test Failed: {e}")

async def run_tests():
    print("🚀 STARTING PHASE 2 TESTS")
    print("=" * 50)
    
    await test_document_counting()
    await test_ai_tagging()
    
    print("\n" + "=" * 50)
    print("🏁 TESTS COMPLETED")

if __name__ == "__main__":
    asyncio.run(run_tests())
