
import os
import sys
from dotenv import load_dotenv
from pinecone import Pinecone

# Load environment variables
load_dotenv(override=True)

api_key = os.getenv("PINECONE_API_KEY")
index_name = os.getenv("PINECONE_INDEX_NAME")

if not api_key:
    print("Error: PINECONE_API_KEY not found in environment.")
    sys.exit(1)

print(f"Connecting to Pinecone index: {index_name}...")
pc = Pinecone(api_key=api_key)
index = pc.Index(index_name)

def inspect_vectors():
    print("\n--- Searching for Analysis Markers ---")
    dummy_vector = [0.0] * 1536
    
    # Try filtering for common analysis tags
    potential_tags = ["analyzed", "claude", "theme", "pattern", "synthesis", "processed"]
    
    found_any = False
    
    for tag_query in potential_tags:
        print(f"\nChecking for tag containing '{tag_query}'...")
        try:
            # We can't easily filter by "contains" in Pinecone metadata (it's exact match usually),
            # but we can try to find *anything* by asking for more results and filtering locally 
            # OR we can try to search for text that might be in an analysis result
            
            # Let's try searching text for "Analysis" or "Theme" which might be in the chunk text if it was an analysis chunk
            # BUT analysis usually updates metadata of EXISTING chunks.
            
            # Strategy: Query a large batch and exhaustive check
            results = index.query(
                vector=dummy_vector,
                top_k=500, # Get more
                include_metadata=True
            )
            
            for match in results.matches:
                md = match.metadata
                tags = md.get('tags', [])
                title = md.get('title', 'Unknown')
                
                has_marker = False
                
                # Check tags list for partial matches
                if isinstance(tags, list):
                    for t in tags:
                        if tag_query.lower() in str(t).lower():
                            has_marker = True
                            print(f"[FOUND TAG MATCH] Doc: {title} | Tag: {t}")

                # Check keys
                for key in md.keys():
                    if tag_query.lower() in key.lower():
                        has_marker = True
                        print(f"[FOUND KEY MATCH] Doc: {title} | Key: {key}")
                        
                if has_marker:
                    found_any = True
                    
        except Exception as e:
            print(f"Error querying: {e}")
            
    if not found_any:
        print("\nNo analysis markers found in 500 vector sample.")


if __name__ == "__main__":
    inspect_vectors()
