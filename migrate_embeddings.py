#!/usr/bin/env python3
import os
import sys
import time
import sqlite3
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
from openai import OpenAI

# Load backend environment variables with override=True
load_dotenv('/Users/carriehuff/consciousness-RAG/consciousness-rag/backend/.env', override=True)

# Validate API keys
pinecone_key = os.getenv("PINECONE_API_KEY")
openai_key = os.getenv("OPENAI_API_KEY")

if not pinecone_key or not openai_key:
    print("❌ Error: Missing PINECONE_API_KEY or OPENAI_API_KEY in backend/.env file.")
    sys.exit(1)

# Initialize Pinecone and OpenAI
print("Initializing Pinecone and OpenAI clients...")
pc = Pinecone(api_key=pinecone_key)
openai_client = OpenAI(api_key=openai_key)

old_index_name = "evolve-consciousness"
new_index_name = "evolve-consciousness-v3"
new_dimension = 3072

# Check if old index exists
existing_indexes = [idx.name for idx in pc.list_indexes()]
if old_index_name not in existing_indexes:
    print(f"❌ Error: Old index '{old_index_name}' does not exist.")
    sys.exit(1)

old_index = pc.Index(old_index_name)

# Retrieve list of documents from SQLite
db_path = '/Users/carriehuff/consciousness-RAG/consciousness-rag/backend/consciousness.db'
if not os.path.exists(db_path):
    print(f"❌ Error: SQLite database not found at {db_path}.")
    sys.exit(1)

conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
docs = conn.execute("SELECT title, chunk_count FROM documents").fetchall()
conn.close()

if not docs:
    print("⚠️ Warning: No documents found in SQLite database.")
    sys.exit(0)

print(f"Loaded {len(docs)} documents from SQLite for migration.")

# Create the new index if it doesn't exist
if new_index_name not in existing_indexes:
    print(f"Creating new Pinecone index: '{new_index_name}' with dimension {new_dimension}...")
    pc.create_index(
        name=new_index_name,
        dimension=new_dimension,
        metric="cosine",
        spec=ServerlessSpec(
            cloud="aws",
            region="us-east-1"
        )
    )
    # Wait for the index to initialize
    print("Waiting for new index initialization...")
    while not pc.describe_index(new_index_name).status.ready:
        time.sleep(2)
    print("✅ Index ready!")
else:
    print(f"Using existing index: '{new_index_name}'")

new_index = pc.Index(new_index_name)

print("\n🚀 Starting vector migration...")

# Process document by document
for idx, doc in enumerate(docs):
    title = doc["title"]
    expected_chunks = doc["chunk_count"]
    print(f"\n[{idx+1}/{len(docs)}] Migrating '{title}' (Expected chunks: {expected_chunks})")
    
    # Query all vectors for this document from the old index
    query_vector = [0.1] * 1536
    try:
        results = old_index.query(
            vector=query_vector,
            filter={"title": title},
            top_k=10000,
            include_metadata=True
        )
        
        matches = results.matches
        if not matches:
            print(f"  ⚠️ No vectors found in old Pinecone index for '{title}'. Skipping...")
            continue
            
        print(f"  Found {len(matches)} vectors in old index.")
        
        # Sort matches by chunk_index to maintain ordering
        matches_sorted = sorted(matches, key=lambda m: m.metadata.get("chunk_index", 0))
        
        vectors_to_upsert = []
        batch_size = 20
        
        for m_idx, match in enumerate(matches_sorted):
            text = match.metadata.get("text", "")
            chunk_idx = match.metadata.get("chunk_index", 0)
            
            # Generate new embedding with text-embedding-3-large (3072 dimensions)
            try:
                emb_resp = openai_client.embeddings.create(
                    model="text-embedding-3-large",
                    input=text
                )
                embedding = emb_resp.data[0].embedding
                
                # Clone metadata and update info
                metadata = dict(match.metadata)
                metadata["ai_model"] = "text-embedding-3-large"
                metadata["schema_version"] = 2
                
                vectors_to_upsert.append({
                    "id": match.id,
                    "values": embedding,
                    "metadata": metadata
                })
            except Exception as emb_err:
                print(f"  ❌ Failed to generate embedding for chunk {chunk_idx}: {emb_err}")
                continue
                
            # Upsert in batches
            if len(vectors_to_upsert) >= batch_size or m_idx == len(matches_sorted) - 1:
                if vectors_to_upsert:
                    try:
                        new_index.upsert(vectors=vectors_to_upsert)
                        print(f"  Upserted batch of {len(vectors_to_upsert)} vectors (Progress: {m_idx + 1}/{len(matches_sorted)})...")
                        vectors_to_upsert = []
                        time.sleep(0.2)  # Rate limiting safety pause
                    except Exception as ups_err:
                        print(f"  ❌ Failed to upsert batch: {ups_err}")
                        sys.exit(1)
        
        print(f"  ✅ Successfully migrated '{title}'")
        
    except Exception as e:
        print(f"  ❌ Error fetching vectors for '{title}': {e}")
        continue

print("\n" + "="*50)
print("🎉 VECTOR MIGRATION COMPLETED SUCCESSFULLY!")
print(f"All documents have been re-embedded and uploaded to: {new_index_name}")
print("="*50 + "\n")
