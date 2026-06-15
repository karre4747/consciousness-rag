import asyncio
import os
import sys
from dotenv import load_dotenv
load_dotenv()

from pinecone import Pinecone
from openai import OpenAI
from anthropic import Anthropic

# Initialize Clients manually for script
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index(os.getenv("PINECONE_INDEX_NAME"))
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

import tagging
import database
import logging

# Mock or import items from main
from main import pinecone_with_retry, PINECONE_DIMENSION, claude_second_pass_analysis

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("force_process")

async def force_tagging(title):
    logger.info(f"Forcing AI Tagging for: {title}")
    query_vector = [0.0] * PINECONE_DIMENSION
    
    # Get chunks from Pinecone
    res = await pinecone_with_retry(
        lambda: index.query(vector=query_vector, top_k=500, include_metadata=True, filter={"title": title})
    )
    
    matches = res.matches
    if not matches:
        logger.error(f"No chunks found for {title}")
        return

    logger.info(f"Found {len(matches)} chunks for tagging")
    
    for m in matches:
        text = m.metadata.get('text', '')
        if not text: continue
        
        # Generate OpenAI tags
        logger.info(f"Tagging chunk {m.id}...")
        try:
            tags = await tagging.generate_tags(
                text, 
                use_ai=True, 
                ai_provider='openai',
                openai_client=openai_client,
                title=title
            )
            
            # Update metadata
            new_metadata = m.metadata.copy()
            for k, v in tags.items():
                new_metadata[k] = v
            new_metadata['pass_2_status'] = 'OPENAI'
            
            # Upsert back to Pinecone
            index.upsert(vectors=[{
                "id": m.id,
                "values": [0.0] * PINECONE_DIMENSION, # Placeholder (serverless ignores values anyway if only metadata updated, but we need to provide them)
                "metadata": new_metadata
            }])
        except Exception as e:
            logger.error(f"Failed to tag chunk {m.id}: {e}")

    database.update_status(title, "tagged", "OPENAI")
    logger.info(f"Successfully tagged {title}")

async def force_analysis(title):
    logger.info(f"Forcing Claude Analysis for: {title}")
    query_vector = [0.0] * PINECONE_DIMENSION
    
    # Get chunks from Pinecone
    res = await pinecone_with_retry(
        lambda: index.query(vector=query_vector, top_k=500, include_metadata=True, filter={"title": title})
    )
    
    matches = res.matches
    if not matches:
        logger.error(f"No chunks found for {title}")
        return
        
    logger.info(f"Found {len(matches)} chunks for analysis")
    
    # Sort chunks
    sorted_chunks = sorted(matches, key=lambda x: int(x.id.split('_')[-1]) if '_' in x.id else 0)
    full_text = "\n".join([m.metadata.get('text', '') for m in sorted_chunks])
    
    # Run Claude Analysis
    doc_data = {
        "title": title,
        "text": full_text,
        "tags": list(set([t for m in matches for t in m.metadata.get('tags', []) if isinstance(t, str)]))
    }
    
    try:
        logger.info(f"Calling Claude for {title}...")
        results = claude_second_pass_analysis([doc_data])
        
        # Update database
        database.update_status(title, "analyzed")
        logger.info(f"Successfully analyzed {title}")
    except Exception as e:
        logger.error(f"Failed to analyze {title}: {e}")

async def main():
    # 1. Fix the tagging for the Outline
    await force_tagging('90 Day Addiction Program-Outline.pdf')
    
    # 2. Fix the analysis for the Transcending doc
    await force_analysis('728046965-1281-Transcending-The-Levels-Of-Consciousness-David-R-Hawkins-IND')

if __name__ == "__main__":
    asyncio.run(main())
