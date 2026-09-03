#!/usr/bin/env python3
"""
Evolve Consciousness Engine - Batch Claude Synthesis (Pass 3)

Runs cross-document Claude analysis across all documents in the corpus in batches of 5.
Stores the rich synthesis (themes, consciousness patterns, synthesis opportunities,
and cross-document connections) directly into Neon PostgreSQL / SQLite.

Usage:
    # Dry run / test single batch of 5 docs:
    python tools/analyze_all.py --limit 5

    # Run full corpus analysis:
    python tools/analyze_all.py

    # Resume from previous progress:
    python tools/analyze_all.py --resume
"""

import os
import sys
import json
import time
import argparse
from typing import List, Dict, Any

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND = os.path.join(REPO, "backend")
sys.path.insert(0, BACKEND)

from dotenv import load_dotenv
load_dotenv(os.path.join(BACKEND, ".env"), override=True)

import database
from tagging import claude_second_pass_analysis
from pinecone import Pinecone

CHECKPOINT_FILE = os.path.join(REPO, "tools", "analysis_checkpoint.json")

def load_checkpoint():
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE) as f:
            return json.load(f)
    return {"completed_docs": []}

def save_checkpoint(state):
    with open(CHECKPOINT_FILE, "w") as f:
        json.dump(state, f, indent=2)

def main():
    ap = argparse.ArgumentParser(description="Run Claude cross-document analysis across corpus")
    ap.add_argument("--batch-size", type=int, default=5, help="Number of documents to send to Claude per batch")
    ap.add_argument("--limit", type=int, help="Limit total documents to process")
    ap.add_argument("--resume", action="store_true", help="Resume from checkpoint")
    args = ap.parse_args()

    state = load_checkpoint() if args.resume else {"completed_docs": []}
    completed_set = set(state["completed_docs"])

    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    index = pc.Index(os.getenv("PINECONE_INDEX_NAME"))

    docs = database.get_all_documents()
    print(f"Total documents registered: {len(docs)}", flush=True)

    pending_docs = [d for d in docs if d["title"] not in completed_set and (not d.get("analysis_results") or not args.resume)]
    if args.limit:
        pending_docs = pending_docs[:args.limit]

    print(f"Processing {len(pending_docs)} pending documents in batches of {args.batch_size}...", flush=True)
    print("=" * 60, flush=True)

    for i in range(0, len(pending_docs), args.batch_size):
        batch = pending_docs[i:i + args.batch_size]
        batch_titles = [d["title"] for d in batch]
        print(f"\n[Batch {i // args.batch_size + 1}] Analyzing {len(batch)} documents:", flush=True)
        for t in batch_titles:
            print(f"  - {t}", flush=True)

        # Pull sample text chunks from Pinecone for each document to provide rich context to Claude
        doc_payloads = []
        for d in batch:
            title = d["title"]
            chunk_count = d.get("chunk_count", 1)
            # Fetch up to 5 representative chunks (first, middle, last)
            indices = list(dict.fromkeys([0, chunk_count // 4, chunk_count // 2, (3 * chunk_count) // 4, max(0, chunk_count - 1)]))
            vector_ids = [f"{title}-{idx}" for idx in indices if idx < chunk_count]
            
            try:
                fetched = index.fetch(ids=vector_ids)
                texts = [vec.metadata.get("text", "") for vid, vec in fetched.vectors.items() if vec.metadata]
                combined_text = "\n\n".join(texts)
                doc_payloads.append({
                    "id": title,
                    "title": title,
                    "text": combined_text,
                    "tags": []
                })
            except Exception as e:
                print(f"  Error fetching context for {title}: {e}", flush=True)

        if not doc_payloads:
            print("  Skipping batch (no text found).", flush=True)
            continue

        print("  Calling Claude Sonnet for deep cross-document synthesis...", flush=True)
        analysis_result = claude_second_pass_analysis(doc_payloads, batch_size=len(doc_payloads))

        if "error" in analysis_result:
            print(f"  ❌ Claude Analysis Error: {analysis_result['error']}", flush=True)
            continue

        # Save analysis to database for each document in the batch
        for d in batch:
            title = d["title"]
            database.save_analysis(title, analysis_result)
            completed_set.add(title)

        state["completed_docs"] = list(completed_set)
        save_checkpoint(state)
        print(f"  ✅ Saved analysis with {len(analysis_result.get('cross_document_themes', []))} themes and {len(analysis_result.get('suggested_connections', []))} connections!", flush=True)

        time.sleep(1)

    print("\n" + "=" * 60, flush=True)
    print("🎉 Claude Cross-Document Analysis Run Complete!", flush=True)
    print("=" * 60, flush=True)

if __name__ == "__main__":
    main()
