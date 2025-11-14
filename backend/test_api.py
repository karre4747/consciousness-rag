#!/usr/bin/env python3
"""
Test script for Evolve Consciousness Engine API
Demonstrates upload and query functionality
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_upload():
    """Test document upload endpoint"""
    print("\n=== Testing Document Upload ===\n")
    
    # Sample document about the 12 steps and consciousness
    sample_doc = {
        "text": """
        The First Step of recovery is a profound spiritual practice. When we admit powerlessness 
        over addiction, we are actually engaging in a form of surrender that opens the heart chakra. 
        This admission is not weakness - it is the beginning of true strength and consciousness expansion.
        
        Modern neuroscience confirms what mystics have known for millennia: the act of surrender 
        activates the prefrontal cortex and reduces activity in the fear-based amygdala. This is 
        the same mechanism described in the Bhagavad Gita as "letting go of the fruits of action."
        
        The 12 Steps are not just a recovery program - they are an ascension path, a mystical journey 
        that parallels the Kabbalistic Tree of Life, the Buddhist Noble Eightfold Path, and the 
        Hermetic principles of transformation. Each step corresponds to a different level of 
        consciousness on the Hawkins Scale, moving from shame and fear toward courage, acceptance, 
        and ultimately, love and peace.
        
        When we work Step One, we are engaging with the Law of Attraction at its deepest level. 
        By acknowledging our powerlessness, we create space for a Higher Power to enter. This is 
        quantum physics in action - the observer effect shows us that consciousness collapses the 
        wave function. Our surrender is the observation that allows divine intervention to manifest.
        """,
        "title": "The First Step as Spiritual Awakening",
        "source": "Evolve Consciousness Training - Beginner Level",
        "program_level": "beginner",
        "use_ai_tagging": False
    }
    
    response = requests.post(f"{BASE_URL}/upload", json=sample_doc)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Upload successful!")
        print(f"  - Document: {sample_doc['title']}")
        print(f"  - Chunks created: {result['chunks_created']}")
        print(f"  - Vectors uploaded: {result['vectors_uploaded']}")
        return True
    else:
        print(f"✗ Upload failed: {response.status_code}")
        print(f"  Error: {response.text}")
        return False


def test_query():
    """Test query endpoint"""
    print("\n=== Testing Query Endpoint ===\n")
    
    # Sample query
    query = {
        "question": "How does the First Step relate to consciousness and spirituality?",
        "program_level": "beginner",
        "top_k": 3
    }
    
    response = requests.post(f"{BASE_URL}/query", json=query)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Query successful!")
        print(f"\n📝 Question: {query['question']}\n")
        print(f"💡 Answer:\n{result['answer']}\n")
        print(f"📚 Sources used: {len(result['sources'])}")
        for i, source in enumerate(result['sources'], 1):
            print(f"  {i}. {source['title']} (score: {source['score']:.3f})")
        return True
    else:
        print(f"✗ Query failed: {response.status_code}")
        print(f"  Error: {response.text}")
        return False


def test_stats():
    """Test stats endpoint"""
    print("\n=== Database Statistics ===\n")
    
    response = requests.get(f"{BASE_URL}/stats")
    
    if response.status_code == 200:
        stats = response.json()
        print(f"Index: {stats['index_name']}")
        print(f"Total vectors: {stats['total_vectors']}")
        print(f"Dimension: {stats['dimension']}")
        return True
    else:
        print(f"✗ Stats retrieval failed: {response.status_code}")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("  EVOLVE CONSCIOUSNESS ENGINE - API TEST")
    print("=" * 60)
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"\n✓ Server is online: {response.json()['status']}")
    except requests.exceptions.ConnectionError:
        print("\n✗ Error: Server is not running!")
        print("  Start the server with: python main.py")
        return
    
    # Run tests
    upload_success = test_upload()
    
    if upload_success:
        # Wait a moment for indexing
        print("\n⏳ Waiting for indexing to complete...")
        time.sleep(3)
        
        test_query()
        test_stats()
    
    print("\n" + "=" * 60)
    print("  TEST COMPLETE")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
