#!/usr/bin/env python3
"""
Process everything dropped into library/_dropbox/ into the evolveAI library.

Karre drops a file into books/, articles/ or worksheets/ and runs this. The
folder IS the doc_type -- her placement is ground truth, which matters because
the model previously invented 20 different labels for 346 documents, including
both "conference program" and "conference programme".

    extract -> quality gate -> clean OCR artifacts -> Chonkie chunk
            -> metadata + framework mappings -> embed -> Pinecone + SQLite

Ingested files move to _processed/. Files with no extractable text move to
_needs_ocr/ rather than entering the index as empty, unfindable records.

Usage:
    python tools/watch_library.py            # process what is waiting
    python tools/watch_library.py --dry-run  # report only
"""

import argparse
import os
import shutil
import subprocess
import sys

TOOLS = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(TOOLS)
DROPBOX = os.path.join(REPO, "library", "_dropbox")
FORMATS = ("books", "articles", "worksheets")

# The folder name maps to the doc_type written into every chunk's metadata.
FOLDER_TO_TYPE = {
    "books": "book",
    "articles": "article",
    "worksheets": "worksheet",
}


def pending():
    """Return [(path, doc_type)] for every file waiting in a format folder."""
    out = []
    for folder in FORMATS:
        d = os.path.join(DROPBOX, folder)
        if not os.path.isdir(d):
            continue
        for name in sorted(os.listdir(d)):
            if name.startswith(".") or name == "README.md":
                continue
            path = os.path.join(d, name)
            if os.path.isfile(path):
                out.append((path, FOLDER_TO_TYPE[folder]))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    files = pending()
    if not files:
        print("nothing waiting in library/_dropbox/")
        return

    print(f"{len(files)} file(s) waiting:")
    for path, doc_type in files:
        print(f"  [{doc_type:9}] {os.path.basename(path)[:60]}")
    if args.dry_run:
        print("\n(dry run -- nothing processed)")
        return

    # Build a manifest ingest.py understands, with doc_type taken from the
    # folder rather than inferred.
    import csv
    sys.path.insert(0, TOOLS)
    from known_authors import match_shorthand, match_author, is_excluded

    manifest = os.path.join(DROPBOX, ".manifest.csv")
    cols = ["filename", "title", "author", "work", "doc_type", "collection",
            "is_own_content", "topics", "duplicate_of", "size_kb", "path"]
    rows = []
    for path, doc_type in files:
        name = os.path.basename(path)
        if is_excluded(path):
            print(f"  skipping excluded: {name[:56]}")
            continue
        author, work, _ = match_shorthand(name)
        author = author or match_author(name) or ""
        rows.append({
            "filename": name, "title": "", "author": author,
            "work": work or "", "doc_type": doc_type, "collection": "",
            "is_own_content": "", "topics": "", "duplicate_of": "",
            "size_kb": round(os.path.getsize(path) / 1024), "path": path,
        })

    if not rows:
        print("nothing to process after exclusions")
        return

    with open(manifest, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)

    python = os.path.join(REPO, "backend", "venv", "bin", "python")
    result = subprocess.run(
        [python, os.path.join(TOOLS, "ingest.py"), "--inventory", manifest],
        cwd=REPO,
    )
    os.remove(manifest)

    if result.returncode != 0:
        print("\ningest failed; files left in place")
        return

    # Quarantined files need OCR before they can be ingested at all.
    quarantined = set()
    qpath = os.path.join(REPO, "quarantine.json")
    if os.path.exists(qpath):
        import json
        try:
            quarantined = {q["path"] for q in json.load(open(qpath))}
        except Exception:
            pass

    moved = ocr_needed = 0
    for row in rows:
        src = row["path"]
        if not os.path.exists(src):
            continue
        dest_dir = os.path.join(DROPBOX,
                                "_needs_ocr" if src in quarantined
                                else "_processed")
        shutil.move(src, os.path.join(dest_dir, os.path.basename(src)))
        if src in quarantined:
            ocr_needed += 1
        else:
            moved += 1

    print(f"\n{moved} file(s) -> _processed/")
    if ocr_needed:
        print(f"{ocr_needed} file(s) -> _needs_ocr/  "
              f"(run: ocrmypdf in.pdf out.pdf, then drop the result back in)")


if __name__ == "__main__":
    main()
