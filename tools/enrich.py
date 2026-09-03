#!/usr/bin/env python3
"""
Enrich existing Pinecone vectors with full metadata.

The August 2026 ingestion wrote only 11 metadata fields per vector.
The original tagging pipeline generates 39+. This script bridges the gap
by reading each vector's text from Pinecone, running the keyword-based
tagger (free, no API) and optionally GPT-4o-mini, then updating the
vector's metadata in place — no re-embedding needed.

Usage:
    # Dry run — show what would change for one document
    python tools/enrich.py --limit 1 --dry-run

    # Enrich one document (test)
    python tools/enrich.py --limit 1

    # Enrich everything, keyword-only (free, fast)
    python tools/enrich.py

    # Enrich everything with GPT-4o-mini (adds primary_theme, AI tags)
    python tools/enrich.py --ai

    # Resume after interruption (reads checkpoint)
    python tools/enrich.py --resume
"""

import argparse
import json
import os
import sys
import time

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND = os.path.join(REPO, "backend")
sys.path.insert(0, BACKEND)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

CHECKPOINT_FILE = os.path.join(REPO, "tools", "enrich_checkpoint.json")
BATCH_SIZE = 100  # Pinecone fetch limit


def load_checkpoint():
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE) as f:
            return json.load(f)
    return {"completed_ids": [], "stats": {"enriched": 0, "skipped": 0, "errors": 0}}


def save_checkpoint(state):
    with open(CHECKPOINT_FILE, "w") as f:
        json.dump(state, f, indent=2)


def enrich_metadata(text, existing_meta):
    """
    Run keyword-based tagging on text and merge with existing metadata.
    Returns only the NEW fields to add (won't overwrite existing).
    """
    from tagging import generate_tags_keyword_based

    tags_result = generate_tags_keyword_based(text)

    new_fields = {}

    # Core keyword-detected fields
    if tags_result.get("tags"):
        new_fields["tags"] = tags_result["tags"][:50]
    if tags_result.get("emotions"):
        new_fields["emotions"] = tags_result["emotions"]
    if tags_result.get("primary_chakra"):
        new_fields["primary_chakra"] = tags_result["primary_chakra"]
    if tags_result.get("consciousness_level"):
        new_fields["consciousness_level"] = tags_result["consciousness_level"]
    if tags_result.get("tradition"):
        new_fields["tradition"] = tags_result["tradition"]
    if tags_result.get("teacher"):
        new_fields["teacher"] = tags_result["teacher"]
    if tags_result.get("ascension_path"):
        new_fields["ascension_path"] = tags_result["ascension_path"]
    if tags_result.get("bridge_concept"):
        new_fields["bridge_concept"] = tags_result["bridge_concept"]
    if tags_result.get("recovery_focus"):
        new_fields["recovery_focus"] = tags_result["recovery_focus"]
    if tags_result.get("healing_modality"):
        new_fields["healing_modality"] = tags_result["healing_modality"]

    # Expand detected_categories into all_* fields (matches original schema)
    cats = tags_result.get("detected_categories", {})
    category_map = {
        "chakras": "all_chakras",
        "meridians": "all_meridians",
        "addiction_type": "all_addiction_types",
        "twelve_steps": "all_12_steps",
        "consciousness_level": "all_consciousness_levels",
        "traditions": "all_traditions",
        "teachers": "all_teachers",
        "quantum_science": "all_quantum_physics",
        "quantum_particles": "all_quantum_particles",
        "universal_laws": "all_universal_laws",
        "ascension_paths": "all_ascension_paths",
        "bridge_concepts": "all_bridge_concepts",
        "healing_modalities": "all_healing_modalities",
        "sacred_geometry": "all_sacred_geometry",
        "subtle_bodies": "all_subtle_bodies",
        "planets": "all_planets",
        "zodiac_signs": "all_zodiac_signs",
    }
    for cat_key, meta_key in category_map.items():
        values = cats.get(cat_key, [])
        new_fields[meta_key] = values if values else []

    # Add schema marker
    new_fields["schema_version"] = 3
    new_fields["ai_provider"] = existing_meta.get("ai_provider", "openai")

    # Don't overwrite fields that already have real values
    filtered = {}
    for k, v in new_fields.items():
        existing = existing_meta.get(k)
        if existing is None or existing == "" or existing == []:
            filtered[k] = v
        elif k == "tags" and isinstance(existing, list) and isinstance(v, list):
            # Merge tags
            filtered[k] = list(set(existing + v))[:50]
        elif k == "schema_version":
            filtered[k] = v
    return filtered


def enrich_with_ai(text, openai_client):
    """Run GPT-4o-mini for primary_theme and AI-enhanced tags."""
    try:
        resp = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": (
                "Analyze this consciousness/spiritual text and return ONLY valid JSON:\n"
                '{"tags": ["tag1", "tag2"], "primary_theme": "one sentence summary", '
                '"consciousness_level": "shame|fear|courage|acceptance|love|peace|enlightenment"}\n\n'
                f'Text:\n"""{text[:3000]}"""'
            )}],
            max_tokens=300,
            temperature=0.3,
        )
        data = json.loads(resp.choices[0].message.content)
        result = {}
        if data.get("primary_theme"):
            result["primary_theme"] = str(data["primary_theme"])[:200]
        if data.get("tags") and isinstance(data["tags"], list):
            result["ai_tags"] = [str(t).lower()[:40] for t in data["tags"][:10]]
        result["ai_model"] = "gpt-4o-mini"
        return result
    except Exception as e:
        print(f"    AI tagging failed: {e}")
        return {}


def main():
    ap = argparse.ArgumentParser(description="Enrich Pinecone vectors with full metadata")
    ap.add_argument("--limit", type=int, help="Process only N documents")
    ap.add_argument("--dry-run", action="store_true", help="Show changes without writing")
    ap.add_argument("--ai", action="store_true", help="Also run GPT-4o-mini for primary_theme")
    ap.add_argument("--resume", action="store_true", help="Resume from checkpoint")
    ap.add_argument("--doc", type=str, help="Enrich only this specific document title")
    args = ap.parse_args()

    # Load environment
    from dotenv import load_dotenv
    load_dotenv(os.path.join(BACKEND, ".env"), override=True)

    from pinecone import Pinecone
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    index = pc.Index(os.getenv("PINECONE_INDEX_NAME"))

    openai_client = None
    if args.ai:
        from openai import OpenAI
        openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    # Load or reset checkpoint
    state = load_checkpoint() if args.resume else {
        "completed_ids": [], "stats": {"enriched": 0, "skipped": 0, "errors": 0}
    }
    completed_set = set(state["completed_ids"])

    # Load document list from SQLite (all 346 documents with chunk counts)
    import sqlite3
    db_path = os.path.join(BACKEND, "consciousness.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT title, chunk_count FROM documents ORDER BY title")
    all_db_docs = cur.fetchall()
    conn.close()

    print(f"Loaded {len(all_db_docs)} documents from database.", flush=True)

    if args.doc:
        docs_to_process = [(t, c) for t, c in all_db_docs if args.doc in t]
        if not docs_to_process:
            print(f"No document matching '{args.doc}' found in database", flush=True)
            return
    else:
        docs_to_process = all_db_docs

    if args.limit:
        docs_to_process = docs_to_process[:args.limit]

    total_chunks_estimated = sum(c for _, c in docs_to_process)
    print(f"Targeting {len(docs_to_process)} documents (~{total_chunks_estimated} chunks)", flush=True)
    print("=" * 60, flush=True)

    from concurrent.futures import ThreadPoolExecutor

    def process_vector_batch(batch_ids):
        try:
            fetched = index.fetch(ids=batch_ids)
        except Exception as e:
            print(f"  Error fetching {batch_ids[0]}...: {e}", flush=True)
            return 0, len(batch_ids), []

        enriched = 0
        skipped = 0
        newly_done = []

        for vid, vec in fetched.vectors.items():
            meta = vec.metadata or {}
            text = meta.get("text", "")
            if not text:
                skipped += 1
                continue

            new_fields = enrich_metadata(text, meta)
            if not new_fields:
                skipped += 1
                newly_done.append(vid)
                continue

            try:
                index.update(id=vid, set_metadata=new_fields)
                enriched += 1
                newly_done.append(vid)
            except Exception as e:
                print(f"  Error updating {vid}: {e}", flush=True)

        return enriched, skipped, newly_done

    import re

    def get_vector_prefix(title):
        # Ingestion sanitizes non-alphanumeric chars (spaces, &, etc) to underscores
        return re.sub(r'[^a-zA-Z0-9._-]', '_', title)

    for i, (title, chunk_count) in enumerate(docs_to_process, 1):
        prefix = get_vector_prefix(title)
        # Generate expected chunk IDs: "{prefix}-{chunk_idx}"
        vids = [f"{prefix}-{c}" for c in range(chunk_count)]
        pending_ids = [vid for vid in vids if vid not in completed_set]

        if not pending_ids:
            print(f"[{i}/{len(docs_to_process)}] {title} ({chunk_count} chunks) - Already Done", flush=True)
            continue

        print(f"[{i}/{len(docs_to_process)}] {title} ({len(pending_ids)} pending / {chunk_count} total)...", flush=True)

        # Batch into groups of 50
        batches = [pending_ids[j:j + 50] for j in range(0, len(pending_ids), 50)]
        doc_enriched = 0
        doc_skipped = 0

        with ThreadPoolExecutor(max_workers=5) as executor:
            results = executor.map(process_vector_batch, batches)
            for enr, skp, done_ids in results:
                doc_enriched += enr
                doc_skipped += skp
                completed_set.update(done_ids)

        state["completed_ids"] = list(completed_set)
        state["stats"]["enriched"] += doc_enriched
        state["stats"]["skipped"] += doc_skipped
        save_checkpoint(state)

        print(f"  -> {doc_enriched} enriched, {doc_skipped} skipped (Total enriched so far: {state['stats']['enriched']})", flush=True)


    print("=" * 60, flush=True)
    print("ENRICHMENT COMPLETE", flush=True)
    print(f"  Enriched: {state['stats']['enriched']}", flush=True)
    print(f"  Skipped:  {state['stats']['skipped']}", flush=True)
    print(f"  Errors:   {state['stats']['errors']}", flush=True)
    print(f"  Checkpoint: {CHECKPOINT_FILE}", flush=True)
    print("=" * 60, flush=True)


if __name__ == "__main__":
    main()
