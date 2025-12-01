#!/usr/bin/env python3
"""
Accurate cost estimation for Claude API based on actual token counts
"""

import tiktoken
from typing import List, Dict, Any

# Use GPT-4 tokenizer (similar to Claude's)
encoding = tiktoken.encoding_for_model("gpt-4")

def count_tokens(text: str) -> int:
    """Count exact tokens in text"""
    return len(encoding.encode(text))

def estimate_pages(token_count: int) -> int:
    """Estimate page count from tokens (650 tokens ≈ 1 page)"""
    return round(token_count / 650)

def estimate_claude_cost(
    documents: List[Dict[str, Any]],
    batch_size: int = 15
) -> Dict[str, Any]:
    """
    Calculate real cost based on actual document token counts

    Args:
        documents: List of doc chunks from Pinecone query
        batch_size: How many docs per Claude call (default: 15 for granular progress)

    Returns:
        Detailed cost breakdown with token counts
    """

    # Count actual tokens
    total_input_tokens = 0
    doc_count = len(documents)

    for doc in documents:
        text = doc.get('metadata', {}).get('text', '')
        total_input_tokens += count_tokens(text)

    # Estimate output tokens (Claude's response is usually 5-10% of input)
    estimated_output_tokens = int(total_input_tokens * 0.075)  # 7.5% average

    # Calculate costs (Claude Sonnet 4.5 pricing)
    INPUT_COST_PER_1M = 3.00
    OUTPUT_COST_PER_1M = 15.00

    input_cost = (total_input_tokens / 1_000_000) * INPUT_COST_PER_1M
    output_cost = (estimated_output_tokens / 1_000_000) * OUTPUT_COST_PER_1M
    total_cost = input_cost + output_cost

    # Calculate batches
    num_batches = (doc_count + batch_size - 1) // batch_size  # Ceiling division

    # Estimate time (Claude takes ~15-30 seconds per batch with smaller batches)
    estimated_seconds = num_batches * 20  # Average 20 sec per batch
    estimated_minutes = round(estimated_seconds / 60, 1)

    return {
        "total_documents": doc_count,
        "total_chunks": doc_count,
        "estimated_pages": estimate_pages(total_input_tokens),
        "input_tokens": total_input_tokens,
        "estimated_output_tokens": estimated_output_tokens,
        "input_cost": round(input_cost, 2),
        "output_cost": round(output_cost, 2),
        "total_cost": round(total_cost, 2),
        "num_batches": num_batches,
        "batch_size": batch_size,
        "estimated_minutes": estimated_minutes
    }
