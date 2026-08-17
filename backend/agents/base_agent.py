import os
import logging
from typing import Dict, Any, List
from dotenv import load_dotenv
from openai import OpenAI

# Import RAG skills
from skills.multi_angle import multi_angle_search
from skills.citation_builder import build_citations

logger = logging.getLogger(__name__)

# Load backend dotenv configuration
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(BASE_DIR, ".env")
load_dotenv(ENV_PATH, override=True)

# Initialize OpenAI client
openai_key = os.getenv("OPENAI_API_KEY")
openai_client = OpenAI(api_key=openai_key)

class BaseAgent:
    """
    Abstract base class for all specialist query agents.
    Handles RAG search orchestration, prompt assembly, and LLM query generation.
    """
    def __init__(self, name: str, collection_name: str):
        self.name = name
        self.collection_name = collection_name
        self.persona_text = self._load_persona_prompt(name)
        
    def _load_persona_prompt(self, name: str) -> str:
        """Load persona instructions from prompts directory."""
        persona_path = os.path.join(BASE_DIR, "prompts", f"{name}_persona.txt")
        if os.path.exists(persona_path):
            with open(persona_path, "r", encoding="utf-8") as f:
                return f.read().strip()
        logger.warning(f"Persona file not found at {persona_path}. Using empty persona.")
        return ""
        
    def query(self, query_text: str, top_k: int = 15) -> Dict[str, Any]:
        """
        Search the WHOLE library and answer in this agent's voice.

        Collections used to be walls: each agent was filtered to one, so the
        recovery agent structurally could not retrieve neuroscience and the
        science agent could not retrieve inventory practice. That made the
        library's core promise -- cross-domain synthesis -- impossible.

        Retrieval is now unfiltered. The collection becomes a lens on the
        answer (voice, emphasis, which sources lead) rather than a limit on
        what can be found. top_k is 15 rather than 5 because braiding three
        traditions needs passages from more than one book.
        """
        try:
            # Search the entire corpus from several angles; the persona shapes
            # the response but never limits what can be found.
            matches = multi_angle_search(query_text, top_k=top_k)
            
            if not matches:
                return {
                    "status": "no_results",
                    "agent": self.name,
                    "answer": "I scanned the collection but did not find any highly relevant documents to formulate an authoritative answer.",
                    "citations": []
                }
                
            # 3. Build context, surfacing author/tradition/framework metadata.
            # Without this the model sees only filenames and cannot tell that
            # two passages come from different traditions -- which is exactly
            # the connection it is being asked to make.
            context_parts = []
            for m in matches:
                md = m.get("metadata", {}) or {}
                label = md.get("display_title") or m["title"]
                bits = [f"Source: {label}"]
                if md.get("author"):
                    bits.append(f"Author: {md['author']}")
                if md.get("collection"):
                    bits.append(f"Domain: {md['collection']}")
                if md.get("steps"):
                    bits.append(f"12-Step: {', '.join(md['steps'])}")
                if md.get("chakras"):
                    bits.append(f"Chakra: {', '.join(md['chakras'])}")
                if md.get("framework_links"):
                    bits.append(f"Parallels: {', '.join(md['framework_links'])}")
                context_parts.append(" | ".join(bits) + f"\n{m['text']}")
            context_str = "\n\n---\n\n".join(context_parts)
            
            # 4. Construct prompt with context
            prompt = f"""{self.persona_text}

REFERENCE CONTEXT FROM CONSCIOUSNESS LIBRARY:
---
{context_str}
---

USER QUESTION:
{query_text}

INSTRUCTIONS:
Answer the user's question in the voice, authority and tone of your persona.

The sources above deliberately span several traditions -- recovery, metaphysics,
neuroscience, therapeutic practice. Many describe the SAME movement in different
vocabularies. Where the sources genuinely support it, show that connection:
name the parallel and say what it reveals. The 12-Step / chakra / framework
labels above mark where such parallels exist.

Lead with what the user actually asked. Bring in other traditions when they
illuminate the answer, not as a survey -- a knowledgeable friend making a
connection, not a lecture covering every angle.

Ground every claim in the sources and attribute by author or work. Do not
invent facts, and do not force a connection the sources do not support.

ANSWER:"""

            # 5. Call OpenAI Completion (gpt-4o)
            resp = openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1200,
                temperature=0.7
            )
            
            raw_answer = resp.choices[0].message.content.strip()
            
            # 6. Append citations
            citations_markdown = build_citations(matches)
            final_answer = f"{raw_answer}{citations_markdown}"
            
            return {
                "status": "success",
                "agent": self.name,
                "answer": final_answer,
                "citations": matches
            }
            
        except Exception as e:
            logger.error(f"Agent '{self.name}' query failed: {e}")
            return {
                "status": "error",
                "agent": self.name,
                "answer": f"An error occurred while executing the specialist agent: {str(e)}",
                "citations": []
            }
