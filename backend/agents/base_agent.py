import os
import logging
from typing import Dict, Any, List
from dotenv import load_dotenv
from openai import OpenAI

# Import RAG skills
from skills.semantic_search import query_vector_db
from skills.metadata_filter import get_pinecone_filter
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
        
    def query(self, query_text: str, top_k: int = 5) -> Dict[str, Any]:
        """
        Execute collection-filtered semantic search and generate a persona-tailored response.
        """
        try:
            # 1. Get collection-based metadata filters
            filter_dict = get_pinecone_filter(self.collection_name)
            
            # 2. Query Pinecone vector database
            matches = query_vector_db(query_text, top_k=top_k, filter_dict=filter_dict)
            
            if not matches:
                return {
                    "status": "no_results",
                    "agent": self.name,
                    "answer": "I scanned the collection but did not find any highly relevant documents to formulate an authoritative answer.",
                    "citations": []
                }
                
            # 3. Build context string from matches
            context_parts = []
            for m in matches:
                context_parts.append(f"Source Document: {m['title']}\nChunk Snippet:\n{m['text']}")
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
Formulate a comprehensive, highly insightful response to the user's question using the reference context above. Speak with the authority, tone, and directives specified in your persona. Do not make up facts. Focus on practical insights and cross-domain synthesis.

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
