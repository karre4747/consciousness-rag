#!/usr/bin/env python3
"""
Rebuild consciousness.db from Pinecone.

Pinecone holds the vectors AND their metadata, so it is authoritative; SQLite is
a listing cache for the UI and the MCP `list_documents` tool. When ingestion
writes only Pinecone, SQLite silently describes a library that no longer exists
-- 65 documents against an actual 346.

This walks the index, groups vectors by document, and rewrites the rows.

Usage:
    python tools/sync_sqlite.py            # report the difference only
    python tools/sync_sqlite.py --apply    # rewrite the table
"""

import argparse
import os
import sqlite3
import sys
from collections import defaultdict

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(REPO, "backend", "consciousness.db")


def scan_index():
    """Return {title: {chunks, author, collection, doc_type}} from Pinecone."""
    from dotenv import load_dotenv
    from pinecone import Pinecone

    load_dotenv(os.path.join(REPO, "backend", ".env"), override=True)
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    index = pc.Index(os.getenv("PINECONE_INDEX_NAME"))

    ids = []
    for batch in index.list():
        ids.extend(getattr(i, "id", i) for i in batch)
    print(f"index holds {len(ids):,} vectors")

    docs = defaultdict(lambda: {"chunks": 0, "author": "", "collection": "",
                                "doc_type": ""})
    for start in range(0, len(ids), 100):
        fetched = index.fetch(ids=ids[start:start + 100])
        for vec in (getattr(fetched, "vectors", {}) or {}).values():
            md = getattr(vec, "metadata", {}) or {}
            title = md.get("title")
            if not title:
                continue
            d = docs[title]
            d["chunks"] += 1
            for key in ("author", "collection", "doc_type"):
                if not d[key] and md.get(key):
                    d[key] = md[key]
        print(f"  scanned {min(start + 100, len(ids)):,}/{len(ids):,}",
              end="\r", flush=True)
    print()
    return docs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    docs = scan_index()
    print(f"pinecone: {len(docs)} documents")

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    existing = {r[0] for r in cur.execute("SELECT title FROM documents")}
    print(f"sqlite:   {len(existing)} documents")
    print(f"missing from sqlite: {len(set(docs) - existing)}")
    print(f"in sqlite but not in the index: {len(existing - set(docs))}")

    if not args.apply:
        print("\n(report only -- rerun with --apply to rewrite)")
        conn.close()
        return

    cols = {r[1] for r in cur.execute("PRAGMA table_info(documents)")}

    # The index is authoritative: rows for vectors that no longer exist are
    # stale, so replace the table contents rather than merging.
    cur.execute("DELETE FROM documents")
    written = 0
    for title, d in sorted(docs.items()):
        row = {
            "title": title,
            "chunk_count": d["chunks"],
            "status": "analyzed",
            "ai_provider": "openai",
        }
        if "has_keyword_tags" in cols:
            row["has_keyword_tags"] = 1
        if "schema_version" in cols:
            row["schema_version"] = 3
        names = ", ".join(row)
        marks = ", ".join("?" * len(row))
        cur.execute(f"INSERT INTO documents ({names}) VALUES ({marks})",
                    list(row.values()))
        written += 1

    conn.commit()
    total = cur.execute("SELECT COUNT(*), SUM(chunk_count) FROM documents").fetchone()
    conn.close()
    print(f"\nwrote {written} rows -> sqlite now {total[0]} docs, "
          f"{total[1]:,} chunks")


if __name__ == "__main__":
    main()
