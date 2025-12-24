"""
Evolve Consciousness Engine - Three-Pass Tagging System
Complete implementation of Karre's vision:
- Pass 1: Keyword-based tagging (free, fast, structural foundation)
- Pass 2: AI enhancement via Ollama/OpenAI (semantic layer)
- Pass 3: Claude deep analysis (wisdom layer, cross-tradition synthesis)

This is the COMPLETE system as designed - agents will orchestrate it intelligently.
Updated: December 24, 2025
"""

from typing import Dict, Any, List, Optional
import os
from openai import OpenAI
from anthropic import Anthropic
import json
import time

# Import the keyword-based tagging (Pass 1)
from tagging_clean import generate_tags as keyword_tagging


class ThreePassTagger:
    """
    Manages the complete three-tier tagging pipeline.
    Agents will use this class to run all three passes with intelligent orchestration.
    """
    
    def __init__(
        self,
        openai_api_key: Optional[str] = None,
        anthropic_api_key: Optional[str] = None,
        use_ollama: bool = False,
        ollama_base_url: str = "http://localhost:11434"
    ):
        """
        Initialize the three-pass tagger.
        
        Args:
            openai_api_key: OpenAI API key for Pass 2 (if not using Ollama)
            anthropic_api_key: Anthropic API key for Pass 3 (Claude)
            use_ollama: Use local Ollama instead of OpenAI for Pass 2
            ollama_base_url: Base URL for Ollama API
        """
        self.use_ollama = use_ollama
        self.ollama_base_url = ollama_base_url
        
        # Initialize clients
        if not use_ollama and openai_api_key:
            self.openai_client = OpenAI(api_key=openai_api_key)
        else:
            self.openai_client = None
            
        if anthropic_api_key:
            self.anthropic_client = Anthropic(api_key=anthropic_api_key)
        else:
            self.anthropic_client = None
    
    
    def pass_1_keyword_tagging(self, text: str) -> Dict[str, Any]:
        """
        PASS 1: Keyword-based tagging (Free, Fast, Foundation)
        
        Uses Karre's comprehensive 305-line keyword schema covering:
        - Chakras & energy centers
        - Meridians & acupuncture
        - 12 Steps & recovery
        - Consciousness levels (Hawkins)
        - Esoteric traditions
        - Teachers & philosophers
        - Quantum physics
        - Universal laws
        - Ascension paths
        - Sacred geometry
        - Subtle bodies
        - And more...
        
        Returns:
            Dictionary with all detected tags and categories
        """
        return keyword_tagging(text)
    
    
    def pass_2_ai_enhancement(
        self,
        text: str,
        pass_1_tags: Dict[str, Any],
        model: str = "gpt-4o-mini"
    ) -> Dict[str, Any]:
        """
        PASS 2: AI Enhancement (Semantic Layer)
        
        Uses AI to:
        - Catch patterns keywords might miss
        - Understand context and nuance
        - Map synonyms and related concepts
        - Identify implicit themes
        - Suggest additional relevant tags
        
        Args:
            text: The text to analyze
            pass_1_tags: Tags from keyword pass (for context)
            model: Model to use (gpt-4o-mini or ollama model name)
            
        Returns:
            Enhanced tags dictionary with AI-discovered patterns
        """
        if self.use_ollama:
            return self._ai_enhancement_ollama(text, pass_1_tags)
        else:
            return self._ai_enhancement_openai(text, pass_1_tags, model)
    
    
    def _ai_enhancement_openai(
        self,
        text: str,
        pass_1_tags: Dict[str, Any],
        model: str = "gpt-4o-mini"
    ) -> Dict[str, Any]:
        """OpenAI-based Pass 2 enhancement"""
        if not self.openai_client:
            return {"enhanced_tags": [], "semantic_themes": []}
        
        # Truncate text if too long (prevent excessive costs)
        text_sample = text[:3000] if len(text) > 3000 else text
        
        prompt = f"""Analyze this consciousness/spiritual text and identify semantic themes and concepts that might not be caught by keyword matching.

Context from keyword analysis:
{json.dumps(pass_1_tags.get('detected_categories', {}), indent=2)}

Text to analyze:
{text_sample}

Identify:
1. Implicit spiritual/consciousness themes
2. Subtle references to traditions or practices
3. Conceptual connections to quantum physics, mysticism, or recovery
4. Emotional or energetic tone
5. Any additional tags from these categories: chakras, consciousness levels, esoteric traditions, universal laws, healing modalities

Return ONLY valid JSON with this structure:
{{
    "enhanced_tags": ["tag1", "tag2"],
    "semantic_themes": ["theme1", "theme2"],
    "implicit_traditions": ["tradition1"],
    "energy_signature": "description",
    "consciousness_level_detected": "level or null"
}}"""

        try:
            response = self.openai_client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are an expert in consciousness studies, mysticism, and spiritual traditions. Analyze text for deep semantic meaning."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            print(f"Pass 2 OpenAI enhancement error: {e}")
            return {"enhanced_tags": [], "semantic_themes": [], "error": str(e)}
    
    
    def _ai_enhancement_ollama(
        self,
        text: str,
        pass_1_tags: Dict[str, Any],
        model: str = "llama3.2:latest"
    ) -> Dict[str, Any]:
        """Ollama-based Pass 2 enhancement (local, free)"""
        import requests
        
        text_sample = text[:3000] if len(text) > 3000 else text
        
        prompt = f"""Analyze this consciousness/spiritual text for semantic themes.

Keyword tags found: {json.dumps(pass_1_tags.get('detected_categories', {}), indent=2)}

Text: {text_sample}

Identify semantic themes, implicit spiritual concepts, and energy signature. Return JSON only."""

        try:
            response = requests.post(
                f"{self.ollama_base_url}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "format": "json"
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                # Ollama returns {"response": "..."} - parse the response field
                return json.loads(result.get("response", "{}"))
            else:
                return {"enhanced_tags": [], "semantic_themes": [], "error": "Ollama request failed"}
                
        except Exception as e:
            print(f"Pass 2 Ollama enhancement error: {e}")
            return {"enhanced_tags": [], "semantic_themes": [], "error": str(e)}
    
    
    def pass_3_claude_analysis(
        self,
        text: str,
        pass_1_tags: Dict[str, Any],
        pass_2_tags: Dict[str, Any],
        model: str = "claude-sonnet-4-20250514"
    ) -> Dict[str, Any]:
        """
        PASS 3: Claude Deep Analysis (Wisdom Layer)
        
        Uses Claude for:
        - Cross-tradition synthesis
        - Recognition of parallel concepts (moksha = devekut = enlightenment)
        - Deep thematic analysis
        - Consciousness level calibration
        - Training data generation opportunities
        - Connection mapping across documents
        
        This is the highest level of analysis - where the magic happens.
        
        Args:
            text: The text to analyze
            pass_1_tags: Keyword tags
            pass_2_tags: AI-enhanced tags
            model: Claude model to use
            
        Returns:
            Comprehensive analysis with cross-tradition insights
        """
        if not self.anthropic_client:
            return {"wisdom_insights": [], "cross_tradition_links": {}}
        
        # Limit text size for Claude (prevent massive costs)
        text_sample = text[:10000] if len(text) > 10000 else text
        
        prompt = f"""You are analyzing spiritual/consciousness content for the Evolve Consciousness Engine - a comprehensive RAG system bridging 12-Step recovery, mystical traditions, and quantum physics.

KEYWORD TAGS (Pass 1):
{json.dumps(pass_1_tags.get('detected_categories', {}), indent=2)}

AI SEMANTIC ANALYSIS (Pass 2):
{json.dumps(pass_2_tags, indent=2)}

TEXT TO ANALYZE:
{text_sample}

Provide DEEP ANALYSIS covering:

1. **Cross-Tradition Synthesis**: Identify parallel concepts across traditions
   - Example: "moksha (Hindu) = devekut (Kabbalah) = nirvana (Buddhist) = spiritual awakening (12-Step)"
   
2. **Consciousness Calibration**: Estimate Hawkins consciousness level (20-1000)

3. **Quantum-Mystical Bridges**: Connections between quantum physics and spiritual concepts
   - Example: "Observer effect relates to consciousness creating reality"

4. **Recovery Integration**: How does this relate to addiction recovery as ascension?

5. **Training Data Opportunities**: Key prompt/completion pairs for fine-tuning

6. **Wisdom Insights**: Profound realizations or teachings present

Return ONLY valid JSON:
{{
    "consciousness_level": 350,
    "cross_tradition_links": {{
        "concept_name": ["tradition1:term", "tradition2:term"]
    }},
    "quantum_mystical_bridges": ["bridge1", "bridge2"],
    "recovery_ascension_links": ["link1"],
    "wisdom_insights": ["insight1"],
    "training_prompts": [
        {{"prompt": "question", "completion": "answer"}}
    ],
    "overall_theme": "brief description"
}}"""

        try:
            response = self.anthropic_client.messages.create(
                model=model,
                max_tokens=2000,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2
            )
            
            # Extract JSON from response
            content = response.content[0].text
            
            # Try to parse as JSON (Claude should return pure JSON)
            try:
                result = json.loads(content)
            except json.JSONDecodeError:
                # If Claude wrapped in markdown, extract
                if "```json" in content:
                    json_str = content.split("```json")[1].split("```")[0].strip()
                    result = json.loads(json_str)
                else:
                    result = {"error": "Failed to parse Claude response as JSON"}
            
            return result
            
        except Exception as e:
            print(f"Pass 3 Claude analysis error: {e}")
            return {"wisdom_insights": [], "error": str(e)}
    
    
    def run_all_passes(
        self,
        text: str,
        skip_pass_2: bool = False,
        skip_pass_3: bool = False,
        rate_limit_delay: float = 0.0
    ) -> Dict[str, Any]:
        """
        Run all three passes and return comprehensive tagging.
        
        Args:
            text: Text to analyze
            skip_pass_2: Skip AI enhancement (useful for bulk processing to save costs)
            skip_pass_3: Skip Claude analysis (expensive, use for final analysis only)
            rate_limit_delay: Seconds to wait between passes (for rate limiting)
            
        Returns:
            Complete tagging results from all passes
        """
        results = {
            "text_length": len(text),
            "passes_completed": []
        }
        
        # PASS 1: Keywords (always run - free and fast)
        print("Running Pass 1: Keyword tagging...")
        pass_1 = self.pass_1_keyword_tagging(text)
        results["pass_1_keywords"] = pass_1
        results["passes_completed"].append("keyword")
        
        if rate_limit_delay > 0:
            time.sleep(rate_limit_delay)
        
        # PASS 2: AI Enhancement (optional)
        if not skip_pass_2:
            print("Running Pass 2: AI enhancement...")
            pass_2 = self.pass_2_ai_enhancement(text, pass_1)
            results["pass_2_ai_enhanced"] = pass_2
            results["passes_completed"].append("ai_enhanced")
            
            if rate_limit_delay > 0:
                time.sleep(rate_limit_delay)
        else:
            pass_2 = {}
        
        # PASS 3: Claude Analysis (optional - expensive)
        if not skip_pass_3:
            print("Running Pass 3: Claude deep analysis...")
            pass_3 = self.pass_3_claude_analysis(text, pass_1, pass_2)
            results["pass_3_claude_wisdom"] = pass_3
            results["passes_completed"].append("claude_wisdom")
        
        # Merge all tags for easy access
        all_tags = pass_1.get("all_tags", [])
        if "enhanced_tags" in pass_2:
            all_tags.extend(pass_2.get("enhanced_tags", []))
        
        results["merged_tags"] = list(set(all_tags))  # Remove duplicates
        results["tag_count"] = len(results["merged_tags"])
        
        return results


# Convenience function for quick usage
def tag_content_three_pass(
    text: str,
    openai_key: Optional[str] = None,
    anthropic_key: Optional[str] = None,
    use_ollama: bool = False,
    skip_pass_2: bool = False,
    skip_pass_3: bool = False
) -> Dict[str, Any]:
    """
    Quick function to run three-pass tagging.
    
    Usage:
        # All three passes with OpenAI
        results = tag_content_three_pass(text, openai_key="...", anthropic_key="...")
        
        # All three passes with Ollama (free)
        results = tag_content_three_pass(text, anthropic_key="...", use_ollama=True)
        
        # Just keywords (free, fast)
        results = tag_content_three_pass(text, skip_pass_2=True, skip_pass_3=True)
        
        # Keywords + AI (no Claude)
        results = tag_content_three_pass(text, openai_key="...", skip_pass_3=True)
    """
    tagger = ThreePassTagger(
        openai_api_key=openai_key,
        anthropic_api_key=anthropic_key,
        use_ollama=use_ollama
    )
    
    return tagger.run_all_passes(text, skip_pass_2, skip_pass_3)
