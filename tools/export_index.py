#!/usr/bin/env python3
"""
Export every vector in the Pinecone index to disk before a destructive change.

This exists because a misdiagnosed timeout once cost this project 100+
documents. Anything that clears the index must be reversible first.

Writes newline-delimited JSON: one record per vector, with id, metadata and
values. Restore with restore_index.py.

Usage:
    python tools/export_index.py -o backup.jsonl
"""

import argparse
import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-o", "--output", required=True)
    args = ap.parse_args()

    from dotenv import load_dotenv
    from pinecone import Pinecone

    load_dotenv(os.path.join(REPO, "backend", ".env"), override=True)
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    name = os.getenv("PINECONE_INDEX_NAME")
    index = pc.Index(name)

    stats = index.describe_index_stats()
    total = stats.get("total_vector_count", 0)
    print(f"index '{name}': {total:,} vectors, dim {stats.get('dimension')}")
    if not total:
        print("nothing to export")
        return

    written = 0
    with open(args.output, "w", encoding="utf-8") as f:
        # list() paginates ids; fetch() returns values + metadata.
        for id_batch in index.list():
            if not id_batch:
                continue
            # list() yields ListItem objects, not plain strings; fetch()
            # silently returns nothing if handed the objects directly.
            ids = [getattr(item, "id", item) for item in id_batch]
            fetched = index.fetch(ids=ids)
            vectors = getattr(fetched, "vectors", {}) or {}
            for vid, vec in vectors.items():
                f.write(json.dumps({
                    "id": vid,
                    "values": list(getattr(vec, "values", []) or []),
                    "metadata": getattr(vec, "metadata", {}) or {},
                }) + "\n")
                written += 1
            print(f"  exported {written:,}/{total:,}", end="\r", flush=True)

    size_mb = os.path.getsize(args.output) / (1024 * 1024)
    print(f"\nwrote {written:,} vectors -> {args.output} ({size_mb:.1f} MB)")
    if written < total:
        print(f"WARNING: expected {total:,}, got {written:,}. "
              f"Do NOT clear the index.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
