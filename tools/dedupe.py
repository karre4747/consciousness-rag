"""
Pick the best copy when the same work exists in several files.

Duplicates here are not identical bytes. The same book often exists as an
image-only scan, an OCR'd version, and a partial excerpt. Choosing wrongly
means ingesting a PDF with no extractable text at all, which silently yields
an empty or garbage document.

Karre's convention: a filename ending in `-pdf.pdf` means the file WAS an
image and has been OCR'd into readable text. Those win.
"""

import os
import re


def ocr_score(path: str) -> int:
    """Higher is better. Used to choose among copies of the same work."""
    name = os.path.basename(path).lower()
    score = 0

    # Karre's convention: "-pdf.pdf" marks an image that was OCR'd.
    if name.endswith("-pdf.pdf") or name.endswith("_pdf.pdf"):
        score += 100
    if "ocr" in name:
        score += 100

    # A full book beats a chapter or excerpt of it.
    if "full_book" in name or "full-book" in name:
        score += 40

    # Trailing copy markers indicate a duplicate save, not a better version.
    if re.search(r"[ _-](copy|\d)\s*\.[a-z]+$", name):
        score -= 10
    if re.search(r"\(\d+\)", name):
        score -= 10
    if name.startswith("~$"):  # Word lock file, never a real document
        score -= 1000

    return score


def normalize_title(path: str) -> str:
    """
    Reduce a filename to a comparable key for the same underlying work.

    Strips scrape IDs, OCR markers, and copy suffixes so that
    `1950__fleet___rays_of_the_dawn_full_book_OCR.pdf` and
    `1950__fleet___rays_of_the_dawn.pdf` collapse to one key.
    """
    name = os.path.basename(path).lower()
    name = os.path.splitext(name)[0]
    name = re.sub(r"^\d{6,}[-_]", "", name)        # leading scrape id
    name = re.sub(r"[-_]?ocr\b", "", name)
    name = re.sub(r"[-_]?full[-_]?book", "", name)
    name = re.sub(r"[-_]?pdf$", "", name)
    name = re.sub(r"\(\d+\)", "", name)
    name = re.sub(r"[^a-z0-9]+", "", name)
    return name


def choose_best(paths):
    """Return the single best path from a list of copies of one work."""
    return max(paths, key=lambda p: (ocr_score(p), os.path.getsize(p)
                                     if os.path.exists(p) else 0))


def group_and_select(paths):
    """
    Group paths by normalized title and pick a winner per group.

    Returns (keep, drop) lists.
    """
    groups = {}
    for p in paths:
        groups.setdefault(normalize_title(p), []).append(p)

    keep, drop = [], []
    for members in groups.values():
        best = choose_best(members)
        keep.append(best)
        drop.extend(m for m in members if m != best)
    return keep, drop
