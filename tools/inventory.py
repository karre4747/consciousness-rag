#!/usr/bin/env python3
"""
Build a reviewable inventory of the consciousness library.

READ-ONLY. Nothing is moved, renamed, or deleted. The output is a CSV for Karre
to correct before any file is organized or ingested.

For each document it records: content hash (for dedup), real title, author,
work, type, suggested collection, and whether it looks like her own created
content rather than source material.

Identification order, most trustworthy first:
  1. known_authors map  (BHBY -> Dispenza; no model can infer this)
  2. first-page text via a cheap model
  3. keyword fallback

Usage:
    python tools/inventory.py <folder> [<folder> ...] -o inventory.csv
    python tools/inventory.py <folder> --no-ai      # skip model pass (free)
"""

import argparse
import csv
import hashlib
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from known_authors import (
    match_shorthand, match_author, match_collection, is_own_content,
    is_own_worksheet,
)

try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None

try:
    import docx
except ImportError:
    docx = None


def file_hash(path, blocksize=1 << 20):
    """Hash file contents so duplicates are caught regardless of filename."""
    h = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            while chunk := f.read(blocksize):
                h.update(chunk)
    except OSError:
        return None
    return h.hexdigest()[:16]


def extract_first_pages(path, max_chars=2500):
    """Pull the opening text, where title and author almost always appear."""
    ext = os.path.splitext(path)[1].lower()
    try:
        if ext == ".pdf" and PdfReader:
            reader = PdfReader(path)
            parts = []
            for page in reader.pages[:3]:
                parts.append(page.extract_text() or "")
                if sum(len(p) for p in parts) > max_chars:
                    break
            return " ".join(parts)[:max_chars].strip()
        if ext == ".docx" and docx:
            d = docx.Document(path)
            text = " ".join(p.text for p in d.paragraphs[:60])
            return text[:max_chars].strip()
    except Exception:
        return ""
    return ""


def identify_with_ai(client, filename, excerpt):
    """Ask a cheap model to read the excerpt and name the document."""
    if not excerpt or len(excerpt) < 60:
        return {}
    prompt = f"""Identify this document from its opening text.

Filename: {filename}
Opening text:
\"\"\"{excerpt[:2000]}\"\"\"

Return ONLY a JSON object with these keys:
  title      - the real title, not the filename
  author     - author's full name, or "" if genuinely unclear
  work       - the larger book/series this belongs to, or "" if standalone
  doc_type   - one of: book, chapter, transcript, paper, worksheet, article
  topics     - up to 4 short topic keywords

Do not guess an author when the text does not support one. Use "" instead."""
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0,
            response_format={"type": "json_object"},
        )
        return json.loads(resp.choices[0].message.content)
    except Exception as e:
        print(f"    ai failed: {e}", file=sys.stderr)
        return {}


def consolidate_by_work(rows):
    """
    Give every chapter of the same work one shared collection.

    Chapters get classified individually, so a single book scatters: BHBY ch.2
    reads as science_bridge, ch.7 as addiction_recovery, and chapters whose
    titles carry no keyword land nowhere. Fragmenting one book across four
    collections defeats collection-based retrieval, so the work as a whole wins
    by majority vote and chapter-level nuance stays in `topics`.

    Returns the number of rows changed.
    """
    from collections import Counter, defaultdict

    groups = defaultdict(list)
    for r in rows:
        # Group by author+work; fall back to author alone so chapter files that
        # never resolved a `work` string still travel with their siblings.
        # The model sometimes returns JSON null rather than "", so coerce
        # before calling string methods.
        key = ((r["author"] or "").strip().lower(),
               (r["work"] or "").strip().lower())
        if key[0] and r["doc_type"] in ("book", "chapter"):
            groups[key].append(r)

    changed = 0
    for members in groups.values():
        if len(members) < 2:
            continue
        votes = Counter(m["collection"] for m in members if m["collection"])
        if not votes:
            continue
        winner = votes.most_common(1)[0][0]
        for m in members:
            if m["collection"] != winner:
                m["collection"] = winner
                changed += 1
    return changed


def collect_files(folders):
    exts = (".pdf", ".docx", ".epub")
    found = []
    for folder in folders:
        for root, _, files in os.walk(folder):
            if any(s in root for s in ("node_modules", "/venv/", "/.git/")):
                continue
            for name in sorted(files):
                if name.lower().endswith(exts) and not name.startswith("."):
                    found.append(os.path.join(root, name))
    return found


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folders", nargs="+")
    ap.add_argument("-o", "--output", default="inventory.csv")
    ap.add_argument("--no-ai", action="store_true", help="skip the model pass")
    ap.add_argument("--limit", type=int, help="only process the first N files")
    args = ap.parse_args()

    client = None
    if not args.no_ai:
        try:
            from dotenv import load_dotenv
            from openai import OpenAI
            backend_env = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "backend", ".env",
            )
            load_dotenv(backend_env, override=True)
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        except Exception as e:
            print(f"AI disabled ({e}); using filename heuristics only.")

    files = collect_files(args.folders)
    if args.limit:
        files = files[: args.limit]
    print(f"Found {len(files)} documents\n")

    rows, seen = [], {}
    for i, path in enumerate(files, 1):
        name = os.path.basename(path)
        print(f"[{i}/{len(files)}] {name[:66]}")

        digest = file_hash(path)
        duplicate_of = seen.get(digest, "") if digest else ""
        if digest and not duplicate_of:
            seen[digest] = path

        # 1. Known shorthand and authors win over anything a model infers.
        author, work, doc_type = match_shorthand(name)
        if not author:
            author = match_author(name) or ""

        title, topics = "", ""
        # 2. Model pass, only for non-duplicates.
        if client and not duplicate_of:
            excerpt = extract_first_pages(path)
            ai = identify_with_ai(client, name, excerpt)
            # `or ""` throughout: the model may return JSON null for any field.
            title = ai.get("title") or ""
            work = work or ai.get("work") or ""
            doc_type = doc_type or ai.get("doc_type") or ""
            if not author:
                author = ai.get("author") or ""
            t = ai.get("topics", "")
            topics = ", ".join(t) if isinstance(t, list) else str(t)

        # 3. Collection from title/topics/filename, in that order of signal.
        collection = match_collection(" ".join([title, topics, name])) or ""

        rows.append({
            "filename": name,
            "title": title,
            "author": author,
            "work": work,
            "doc_type": doc_type,
            "collection": collection,
            "is_own_content": "YES" if (is_own_content(path)
                                        or is_own_worksheet(path)) else "",
            "topics": topics,
            "duplicate_of": os.path.basename(duplicate_of) if duplicate_of else "",
            "size_kb": round(os.path.getsize(path) / 1024) if os.path.exists(path) else 0,
            "path": path,
        })

    consolidated = consolidate_by_work(rows)

    with open(args.output, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    dupes = sum(1 for r in rows if r["duplicate_of"])
    own = sum(1 for r in rows if r["is_own_content"])
    known = sum(1 for r in rows if r["author"])
    print(f"\nWrote {args.output}")
    print(f"  {len(rows)} documents  |  {dupes} duplicates  |  "
          f"{own} own content  |  {known} with author identified")
    if consolidated:
        print(f"  {consolidated} chapters aligned to their work's collection")


if __name__ == "__main__":
    main()
