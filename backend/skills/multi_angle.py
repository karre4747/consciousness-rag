"""
Multi-angle retrieval.

A single semantic search returns passages closest to how the question happened
to be worded. Ask "CBT, the neuroscience behind it, and how step work
integrates" and the dominant term wins: you get CBT passages, thin neuroscience,
and almost no step work -- so the answer cannot braid the traditions even
though the library holds all three.

This decomposes a request into several angles, searches each independently, and
merges the results. Breadth becomes guaranteed rather than hoped for.

Embeddings cost ~$0.000004 per query, so four searches instead of one is
negligible; the cost is roughly a second of latency.
"""

import logging
from typing import Any, Dict, List

from skills.semantic_search import query_vector_db

logger = logging.getLogger(__name__)

# Standing lenses on the corpus. Each becomes a separate search, so material
# from that tradition is retrieved on its own terms rather than competing with
# the question's dominant vocabulary.
DOMAIN_ANGLES = {
    "recovery": "12-step recovery, inventory work, sponsorship, sobriety",
    "science": "neuroscience, brain, neuroplasticity, clinical research",
    "therapy": "CBT, DBT, EMDR, somatic and trauma-informed practice",
    "spiritual": "meditation, chakras, subtle energy, metaphysical teaching",
}


def build_angles(question: str, extra: List[str] = None) -> List[str]:
    """
    Turn one request into several search phrasings.

    The literal question always leads -- it is the best match for what was
    actually asked. Domain angles follow, and are only added when the question
    does not already sit squarely in that domain.
    """
    angles = [question]

    # Weight each angle toward its domain while keeping the question present.
    # Appending the domain to the full question barely moves the embedding --
    # the question's dominant terms still decide the match. Leading with the
    # domain vocabulary and following with a short form of the question pulls
    # the search into that tradition without losing the topic.
    short = " ".join(question.split()[:12])
    for phrasing in DOMAIN_ANGLES.values():
        angles.append(f"{phrasing}: {short}")

    if extra:
        angles.extend(extra)
    return angles


def merge_matches(result_sets: List[List[Dict[str, Any]]],
                  top_k: int) -> List[Dict[str, Any]]:
    """
    Combine several result sets into one ranked list.

    Deduplicates by vector id, keeping the highest score seen. Then interleaves
    by source document so a single verbose book cannot occupy every slot --
    breadth across works is the whole point of searching several angles.
    """
    best: Dict[str, Dict[str, Any]] = {}
    for matches in result_sets:
        for m in matches:
            prev = best.get(m["id"])
            if prev is None or m["score"] > prev["score"]:
                best[m["id"]] = m

    ranked = sorted(best.values(), key=lambda m: m["score"], reverse=True)

    # Round-robin across documents: take the best remaining chunk from each
    # distinct title in turn, so several works are represented before any one
    # work contributes a second passage.
    by_title: Dict[str, List[Dict[str, Any]]] = {}
    for m in ranked:
        by_title.setdefault(m.get("title", "?"), []).append(m)

    out: List[Dict[str, Any]] = []
    while len(out) < top_k and by_title:
        for title in list(by_title):
            if len(out) >= top_k:
                break
            out.append(by_title[title].pop(0))
            if not by_title[title]:
                del by_title[title]
    return out


def multi_angle_search(question: str, top_k: int = 15,
                       extra_angles: List[str] = None) -> List[Dict[str, Any]]:
    """
    Search the library from several angles and return one merged ranking.

    Each angle retrieves a smaller slice; the merge fills top_k with the
    strongest passages across all of them.
    """
    angles = build_angles(question, extra_angles)
    per_angle = max(4, top_k // 2)

    results = []
    for angle in angles:
        try:
            results.append(query_vector_db(angle, top_k=per_angle,
                                           filter_dict=None))
        except Exception as e:
            logger.warning(f"angle failed ({angle[:40]}...): {e}")

    merged = merge_matches(results, top_k)
    logger.info(f"multi-angle: {len(angles)} searches -> "
                f"{len(merged)} chunks from "
                f"{len({m.get('title') for m in merged})} documents")
    return merged
