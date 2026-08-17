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
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource

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
app = Server("evolve-consciousness-mcp")


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


@app.list_tools()
async def list_tools() -> list[Tool]:
    """
    List available tools.

    Returns:
        List of available MCP tools
    """
    return [
        Tool(
            name="query_consciousness_library",
            description="""Query the evolveAI consciousness library for research on spiritual development, recovery, and mystical wisdom.

This tool provides access to a comprehensive database covering:
- **12-Step Recovery**: All 12 steps, recovery principles, spiritual awakening in addiction recovery
- **Mysticism & Spirituality**: Various mystical traditions (Christian, Sufi, Buddhist, Hindu, Jewish, etc.), contemplative practices, mystical experiences
- **Chakras & Energy**: Seven chakra system, energy centers, kundalini, subtle body anatomy
- **Astrology**: Planetary influences, astrological symbolism, cosmic consciousness
- **Quantum Consciousness**: Quantum physics and consciousness, reality creation, observer effect

Perfect for:
- Course creation and curriculum development
- Research on consciousness and spiritual development
- Finding connections between recovery and mystical traditions
- Exploring chakra-based healing approaches
- Understanding astrological influences on consciousness
- Investigating quantum perspectives on awareness

The library contains teachings from spiritual masters, recovery literature, mystical texts, and consciousness research.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "The research question or topic you want to explore. Be specific and detailed for best results."
                    },
                    "focus_area": {
                        "type": "string",
                        "enum": ["all", "12_steps", "mysticism", "chakras", "astrology", "quantum"],
                        "description": "Optional: Filter results to a specific area of focus. Use 'all' or omit for unrestricted search.",
                        "default": "all"
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "Number of relevant sources to retrieve (default: 5, max recommended: 10)",
                        "default": DEFAULT_TOP_K,
                        "minimum": 1,
                        "maximum": 20
                    }
                },
                "required": ["question"]
            }
        ),
        Tool(
            name="list_documents",
            description="List all available documents in the consciousness library to see what can be queried.",
            inputSchema={
                "type": "object",
                "properties": {},
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent | ImageContent | EmbeddedResource]:
    """
    Handle tool calls.

    Args:
        name: Name of the tool to call
        arguments: Arguments for the tool

    Returns:
        List of content items (text, images, or embedded resources)
    """
    if name == "query_consciousness_library":
        # Extract arguments
        question = arguments.get("question")
        if not question:
            raise ValueError("Question is required")

        focus_area = arguments.get("focus_area", "all")
        top_k = arguments.get("top_k", DEFAULT_TOP_K)

        # Validate top_k
        if top_k < 1 or top_k > 20:
            top_k = DEFAULT_TOP_K

        # Build request payload
        payload = {
            "question": question,
            "top_k": top_k
        }

        # Add filters if focus area is specified
        filters = build_filters(focus_area)
        if filters:
            payload["filters"] = filters

        logger.info(f"Querying consciousness library: question='{question}', focus_area='{focus_area}', top_k={top_k}")

        try:
            # Make request to backend API
            # Increased timeout to 120s to accommodate Claude answer generation (up to 90s)
            response = requests.post(
                QUERY_ENDPOINT,
                json=payload,
                timeout=120
            )
            response.raise_for_status()

            # Parse response
            data = response.json()

            # Format the response
            formatted_output = format_response(data)

            logger.info(f"Successfully retrieved results for question: '{question}'")

            return [
                TextContent(
                    type="text",
                    text=formatted_output
                )
            ]

        except requests.exceptions.Timeout:
            error_msg = "Request to consciousness library timed out. Please try again."
            logger.error(error_msg)
            return [
                TextContent(
                    type="text",
                    text=f"Error: {error_msg}"
                )
            ]

        except requests.exceptions.ConnectionError:
            error_msg = f"Could not connect to consciousness library at {BACKEND_URL}. Please check if the service is running."
            logger.error(error_msg)
            return [
                TextContent(
                    type="text",
                    text=f"Error: {error_msg}"
                )
            ]

        except requests.exceptions.HTTPError as e:
            error_msg = f"HTTP error occurred: {e.response.status_code} - {e.response.text}"
            logger.error(error_msg)
            return [
                TextContent(
                    type="text",
                    text=f"Error: {error_msg}"
                )
            ]

        except json.JSONDecodeError:
            error_msg = "Failed to parse response from consciousness library. Invalid JSON received."
            logger.error(error_msg)
            return [
                TextContent(
                    type="text",
                    text=f"Error: {error_msg}"
                )
            ]

        except Exception as e:
            error_msg = f"Unexpected error occurred: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return [
                TextContent(
                    type="text",
                    text=f"Error: {error_msg}"
                )
            ]

    # Handle list_documents tool
    elif name == "list_documents":
        try:
            # Query the fast SQLite-backed endpoint
            response = requests.get(STATUS_ENDPOINT, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            docs = data.get("documents", [])
            total = data.get("total_documents", 0)
            
            # Format as a list
            doc_list = []
            for d in docs:
                status = "✅"
                if d.get("pass_3_status") != "Complete":
                    status = "⚠️"
                doc_list.append(f"- {status} **{d['title']}** ({d['chunk_count']} chunks)")
            
            formatted_list = f"## Available Documents ({total})\n\n" + "\n".join(doc_list)
            
            return [
                TextContent(
                    type="text",
                    text=formatted_list
                )
            ]
            
        except Exception as e:
            return [TextContent(type="text", text=f"Error listing documents: {str(e)}")]

    raise ValueError(f"Unknown tool: {name}")


async def main():
    """Main entry point for the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        logger.info("Starting evolveAI Consciousness MCP Server")
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
