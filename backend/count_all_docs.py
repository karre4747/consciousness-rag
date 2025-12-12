import os
import asyncio
from pinecone import Pinecone

async def count_unique_docs():
    unique_titles = set()api_key = os.getenv("PINECONE_API_KEY")
    if not api_key:
        raise ValueError("PINECONE_API_KEY environment variable is not set")
    
    pc = Pinecone(api_key=api_key)
    index = pc.Index("consciousness-rag")
    
    print("Scanning database for unique documents...")

async def count_unique_docs():
    print("Scanning database for unique documents...")
    unique_titles = set()
    total_chunks = 0
    
    # Iterate using simple query pagination or just list (Pinecone doesn't allow iterating easily without IDs)
    # But we can query with vector of 0s and fetch stats
    
    stats = index.describe_index_stats()
    print(f"Total Vectors in DB: {stats.total_vector_count}")
    
    # Attempt to fetch broader sample
    # Note: query is limited to 10k. 
    # To get more, we'd need to fetch by ID prefix if we knew it, or namespaces.
    # Assuming all in default namespace.
    
    # We can't easily list all without an external map. 
    # But we can try to query 10k, then exclude those IDs? No, negative filter is expensive/not standard.
    
    results = index.query(
        vector=[0.0]*1536,
        top_k=10000,
        include_metadata=True
    )
    
    for match in results.matches:
        if match.metadata and 'title' in match.metadata:
            unique_titles.add(match.metadata['title'])
    
    print(f"Unique Titles found in top 10k chunks: {len(unique_titles)}")
    print("Titles found:")
    for t in sorted(list(unique_titles)):
        print(f" - {t}")

if __name__ == "__main__":
    asyncio.run(count_unique_docs())
