"""
MCP Server for evolveAI Consciousness Library

This server provides access to a consciousness/recovery content research system
through the Model Context Protocol (MCP).
"""

import asyncio
import json
import logging
import os
from typing import Any, Optional

import requests
from mcp.server import MCPServer
from mcp.types import TextContent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("consciousness-mcp")

# Backend API configuration
# Uses API_URL environment variable if set (from Claude Desktop config), otherwise defaults to localhost
BACKEND_URL = os.environ.get("API_URL", "http://localhost:8001")
QUERY_ENDPOINT = f"{BACKEND_URL}/query"
STATUS_ENDPOINT = f"{BACKEND_URL}/document-status"
DEFAULT_TOP_K = 15  # matches BaseAgent; 5 is too thin for cross-domain synthesis

# Initialize MCP server
app = MCPServer(
    "evolve-consciousness-mcp",
    version="2.0.0",
    instructions=(
        "Access to Karre Huff's consciousness library: recovery, metaphysics, "
        "neuroscience and therapeutic modalities. Retrieval spans the whole "
        "corpus, so answers may braid several traditions."
    ),
)


def build_filters(focus_area: Optional[str] = None) -> dict[str, Any]:
    """
    Build Pinecone filters based on the focus area.

    Args:
        focus_area: Optional focus area for filtering results

    Returns:
        Dictionary of filters to apply to the query
    """
    # Define known values for categories to enable "$in" filtering (Pinecone's "intersects")
    
    # Chakras
    chakras = ["root", "sacral", "solar_plexus", "heart", "throat", "third_eye", "crown", 
               "soul_star", "earth_star"]
               
    # 12 Steps
    steps = [f"step_{i}" for i in range(1, 13)]
    
    # Astrology (Planets + Signs)
    astrology = [
        # Planets
        "sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn", "uranus", "neptune", "pluto",
        # Signs
        "aries", "taurus", "gemini", "cancer", "leo", "virgo", "libra", "scorpio", "sagittarius", 
        "capricorn", "aquarius", "pisces"
    ]
    
    # Quantum Concepts (subset of common tags)
    quantum = [
        "quantum_physics", "entanglement", "superposition", "observer_effect", "wave_particle",
        "zero_point", "frequency", "vibration", "resonance", "photon", "subatomic"
    ]
    
    # Mysticism (Broad traditions)
    traditions = [
        "hermetic", "kabbalah", "sufi", "gnostic", "rosicrucian", "vedic", "buddhist", 
        "taoist", "shamanic", "hindu", "christian_mysticism", "essene"
    ]

    if focus_area == "12_steps":
        return {"all_12_steps": {"$in": steps}}
    
    elif focus_area == "chakras":
        return {"all_chakras": {"$in": chakras}}
        
    elif focus_area == "astrology":
        # Check both planets and signs (requires OR logic which Pinecone supports via multiple queries or complex filter)
        # Pinecone metadata filters don't support top-level OR easily in one query without creating complex condition
        # For simplicity in this demo, we'll check distinct fields using $in if supported, or just one
        # Actually Pinecone standard filtering is AND based. We can't do (A OR B).
        # We will filter for WHERE all_planets has values OR all_zodiac_signs has values.
        # Since we can't do OR, we might have to pick the most likely one or compromise.
        # BETTER STRATEGY: In tagging.py change 'astrology' to be a unified 'all_astrology' field?
        # Too late for that refactor without large cost.
        # Let's just filter for 'all_planets' OR 'all_zodiac_signs' by sending a filter that matches EITHER?
        # No, Pinecone is strict.
        # Let's assume most astrology content mentions planets. We'll filter on `all_planets` for now `all_zodiac_signs` overlap.
        # Actually, let's just use `all_planets` as the primary filter for now as it's more universal.
        return {"all_planets": {"$in": astrology}}
        
    elif focus_area == "quantum":
        return {"all_quantum_concepts": {"$in": quantum}}
        
    elif focus_area == "mysticism":
        return {"all_traditions": {"$in": traditions}}

    return {}


def format_response(data: dict[str, Any]) -> str:
    """
    Format the API response into a readable string with answer, sources, and metadata.

    Args:
        data: Response data from the backend API

    Returns:
        Formatted string with answer and metadata
    """
    output = []

    # Add the main answer
    if "answer" in data:
        output.append("## Answer\n")
        output.append(data["answer"])
        output.append("\n")

    # Add sources with metadata
    if "sources" in data and data["sources"]:
        output.append("\n## Sources\n")
        for idx, source in enumerate(data["sources"], 1):
            output.append(f"\n### Source {idx}")

            # Add content/text
            if "text" in source:
                output.append(f"\n**Content:** {source['text'][:500]}...")
            elif "content" in source:
                output.append(f"\n**Content:** {source['content'][:500]}...")

            # Add metadata if available
            metadata = source.get("metadata", {})

            if metadata.get("all_traditions"):
                output.append(f"\n**Traditions:** {', '.join(metadata['all_traditions'])}")

            if metadata.get("all_teachers"):
                output.append(f"\n**Teachers:** {', '.join(metadata['all_teachers'])}")

            if metadata.get("all_chakras"):
                output.append(f"\n**Chakras:** {', '.join(metadata['all_chakras'])}")

            if metadata.get("all_12_steps"):
                output.append(f"\n**12 Steps:** {', '.join(metadata['all_12_steps'])}")

            if metadata.get("all_planets"):
                output.append(f"\n**Planets:** {', '.join(metadata['all_planets'])}")

            if metadata.get("all_zodiac_signs"):
                output.append(f"\n**Zodiac Signs:** {', '.join(metadata['all_zodiac_signs'])}")

            if metadata.get("all_quantum_concepts"):
                output.append(f"\n**Quantum Concepts:** {', '.join(metadata['all_quantum_concepts'])}")

            if metadata.get("source"):
                output.append(f"\n**Source Document:** {metadata['source']}")

            output.append("\n")

    return "\n".join(output)


QUERY_DESC = """Query the evolveAI consciousness library for research on spiritual development, recovery, and mystical wisdom.

Covers 12-Step recovery, mysticism and contemplative traditions, chakras and
subtle energy, astrology, quantum consciousness, neuroscience, and therapeutic
modalities (CBT, DBT, EMDR, somatic work).

Retrieval searches the entire corpus from several angles at once, so results
deliberately span domains -- useful for course creation, lecture prep, and
finding connections between recovery practice and other traditions."""


@app.tool(name="query_consciousness_library", description=QUERY_DESC)
async def query_consciousness_library(
    question: str,
    focus_area: str = "all",
    top_k: int = DEFAULT_TOP_K,
) -> str:
    """
    Args:
        question: The research question or topic. Be specific for best results.
        focus_area: Optional lens: all, 12_steps, mysticism, chakras, astrology, quantum.
        top_k: Number of sources to retrieve (1-25).
    """
    return await _do_query(question, focus_area, top_k)


@app.tool(
    name="list_documents",
    description="List all documents available in the consciousness library.",
)
async def list_documents() -> str:
    """Return the library's document inventory."""
    return await _do_list_documents()


async def _do_query(question: str, focus_area: str = "all",
                    top_k: int = DEFAULT_TOP_K) -> str:
    """Call the backend /query endpoint and format the result."""
    if not question:
        raise ValueError("Question is required")

    if top_k < 1 or top_k > 25:
        top_k = DEFAULT_TOP_K

    payload = {"question": question, "top_k": top_k}
    filters = build_filters(focus_area)
    if filters:
        payload["filters"] = filters

    logger.info(f"query: {question[:60]!r} focus={focus_area} top_k={top_k}")

    try:
        # Generation can take up to ~90s; keep the client timeout above it.
        response = await asyncio.to_thread(
            requests.post, QUERY_ENDPOINT, json=payload, timeout=120
        )
        response.raise_for_status()
        return format_response(response.json())

    except requests.exceptions.Timeout:
        return "Error: request to the consciousness library timed out."
    except requests.exceptions.ConnectionError:
        return (f"Error: could not connect to the consciousness library at "
                f"{BACKEND_URL}. Is the backend running on port 8001?")
    except requests.exceptions.HTTPError as e:
        return f"Error: HTTP {e.response.status_code} - {e.response.text[:200]}"
    except json.JSONDecodeError:
        return "Error: invalid JSON received from the consciousness library."
    except Exception as e:
        logger.error("unexpected error", exc_info=True)
        return f"Error: {e}"


async def _do_list_documents() -> str:
    """Call the backend /document-status endpoint and format the inventory."""
    try:
        response = await asyncio.to_thread(
            requests.get, STATUS_ENDPOINT, timeout=10
        )
        response.raise_for_status()
        data = response.json()

        docs = data.get("documents", [])
        total = data.get("total_documents", 0)
        lines = []
        for d in docs:
            mark = "OK" if d.get("pass_3_status") == "Complete" else "--"
            lines.append(f"- [{mark}] **{d['title']}** ({d['chunk_count']} chunks)")
        return f"## Available Documents ({total})\n\n" + "\n".join(lines)

    except Exception as e:
        return f"Error listing documents: {e}"


if __name__ == "__main__":
    # mcp 2.x manages the stdio transport itself; no manual stream plumbing.
    logger.info("Starting evolveAI Consciousness MCP Server")
    asyncio.run(app.run_stdio_async())
