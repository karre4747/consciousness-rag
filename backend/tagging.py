#!/usr/bin/env python3
"""
Evolve Consciousness Engine - Enhanced Tagging System with Claude AI
Comprehensive tagging for consciousness, recovery, mysticism, quantum physics, and esoteric teachings
Updated: November 14, 2025
"""

from typing import Dict, Any, List
import os
from anthropic import Anthropic

# Initialize Anthropic client
def get_anthropic_client():
    """Get Anthropic client with API key from environment"""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not found in environment")
    return Anthropic(api_key=api_key)


def generate_tags_keyword_based(text: str) -> Dict[str, Any]:
    """Generate comprehensive consciousness and recovery tags using keyword matching"""
    tags = []
    detected_categories = {}
    text_lower = text.lower()
    
    # === CHAKRAS & ENERGY CENTERS ===
    chakra_keywords = {
        "root": ["survival", "safety", "grounding", "security", "foundation", "muladhara"],
        "sacral": ["creativity", "sexuality", "emotions", "pleasure", "svadhisthana"],
        "solar_plexus": ["power", "will", "confidence", "manipura", "self-esteem"],
        "heart": ["love", "compassion", "forgiveness", "anahata", "connection"],
        "throat": ["communication", "expression", "truth", "vishuddha", "voice"],
        "third_eye": ["intuition", "vision", "insight", "ajna", "perception"],
        "crown": ["consciousness", "enlightenment", "spiritual", "sahasrara", "divine"]
    }
    
    # === ADDICTION & RECOVERY ===
    recovery_keywords = {
        "addiction_type": {
            "alcohol": ["alcohol", "drinking", "sober", "alcoholism"],
            "drugs": ["drugs", "substance", "narcotics", "opioid"],
            "codependency": ["codependent", "relationship addiction", "boundaries"]
        },
        "recovery_stage": {
            "early_recovery": ["early recovery", "newcomer", "first 90 days"],
            "sustained_recovery": ["long-term recovery", "maintenance"],
            "spiritual_awakening": ["spiritual awakening", "transformation", "rebirth"]
        },
        "12_steps": {
            "step_1": ["powerlessness", "unmanageable", "surrender"],
            "step_2": ["higher power", "sanity", "restoration"],
            "step_3": ["decision", "turn over", "will"],
            "step_4": ["moral inventory", "fearless", "resentments"],
            "step_11": ["prayer", "meditation", "conscious contact"],
            "step_12": ["spiritual awakening", "carry message"]
        }
    }
    
    # === CONSCIOUSNESS LEVELS ===
    consciousness_keywords = {
        "shame": ["shame", "humiliation", "worthless"],
        "fear": ["fear", "anxiety", "worry"],
        "courage": ["courage", "affirmation", "empowerment"],
        "acceptance": ["acceptance", "forgiveness", "harmony"],
        "love": ["unconditional love", "reverence", "benevolence"],
        "peace": ["peace", "tranquility", "transcendence"],
        "enlightenment": ["enlightenment", "pure consciousness"]
    }
    
    # === ESOTERIC TRADITIONS ===
    esoteric_keywords = {
        "hermetic": ["hermetic", "hermes", "emerald tablet", "kybalion"],
        "kabbalah": ["kabbalah", "sephiroth", "tree of life", "zohar"],
        "sufi": ["sufi", "rumi", "dhikr", "fana"],
        "vedic": ["vedic", "vedas", "upanishads", "brahman"],
        "buddhist": ["buddhist", "dharma", "noble truths", "nirvana"],
        "taoist": ["tao", "yin yang", "wu wei", "i ching"]
    }
    
    # === TEACHERS ===
    teachers_keywords = {
        "hawkins": ["david hawkins", "power vs force", "letting go"],
        "dispenza": ["joe dispenza", "becoming supernatural", "neuroplasticity"],
        "lipton": ["bruce lipton", "biology of belief", "epigenetics"],
        "goddard": ["neville goddard", "imagination creates reality"],
        "murphy": ["joseph murphy", "power of subconscious"],
        "holmes": ["ernest holmes", "science of mind"]
    }
    
    # === QUANTUM & SCIENCE ===
    quantum_keywords = {
        "quantum_physics": ["quantum", "quantum mechanics", "quantum field"],
        "neuroscience": ["neuroplasticity", "neurotransmitter", "dopamine", "serotonin"],
        "epigenetics": ["epigenetic", "gene expression", "methylation"],
        "biofield": ["biofield", "aura", "electromagnetic", "biophoton"]
    }
    
    # === UNIVERSAL LAWS ===
    universal_laws = {
        "law_of_attraction": ["law of attraction", "manifestation", "magnetism"],
        "law_of_vibration": ["vibration", "frequency", "resonance"],
        "law_of_correspondence": ["as above so below", "microcosm", "macrocosm"],
        "law_of_cause_effect": ["karma", "cause and effect", "consequences"]
    }
    
    # Process all categories
    all_categories = {
        "chakras": chakra_keywords,
        "recovery": recovery_keywords,
        "consciousness_level": consciousness_keywords,
        "esoteric_tradition": esoteric_keywords,
        "teachers": teachers_keywords,
        "quantum_science": quantum_keywords,
        "universal_laws": universal_laws
    }
    
    for category_name, category_dict in all_categories.items():
        detected_categories[category_name] = []
        for tag_name, keywords in category_dict.items():
            if isinstance(keywords, dict):
                # Handle nested dictionaries
                for sub_tag, sub_keywords in keywords.items():
                    if any(keyword in text_lower for keyword in sub_keywords):
                        full_tag = f"{tag_name}:{sub_tag}"
                        detected_categories[category_name].append(full_tag)
                        tags.append(full_tag)
            else:
                # Handle simple keyword lists
                if any(keyword in text_lower for keyword in keywords):
                    detected_categories[category_name].append(tag_name)
                    tags.append(tag_name)
    
    return {
        "tags": list(set(tags)),
        "detected_categories": detected_categories
    }


def generate_tags_ai_enhanced(text: str, max_tokens: int = 500) -> Dict[str, Any]:
    """Generate enhanced tags using Claude AI for deeper semantic understanding"""
    
    prompt = f"""Analyze this text and identify relevant tags from consciousness, recovery, and spiritual domains.

Text to analyze:
{text[:2000]}

Identify tags in these categories:
1. Chakras: root, sacral, solar_plexus, heart, throat, third_eye, crown
2. Recovery: early_recovery, sustained_recovery, spiritual_awakening
3. 12 Steps: step_1, step_2, step_3, step_4, step_11, step_12
4. Consciousness Level: shame, fear, courage, acceptance, love, peace, enlightenment
5. Traditions: hermetic, kabbalah, sufi, vedic, buddhist, taoist
6. Science: quantum_physics, neuroscience, epigenetics, biofield
7. Laws: law_of_attraction, law_of_vibration, law_of_correspondence
8. Program Level: beginner, intermediate, advanced

Return ONLY a JSON object:
{{
  "tags": ["tag1", "tag2"],
  "primary_theme": "main theme",
  "consciousness_level": "level",
  "program_level": "beginner|intermediate|advanced"
}}"""

    try:
        client = get_anthropic_client()
        message = client.messages.create(
            model=os.getenv("CLAUDE_MODEL", "claude-sonnet-4-5-20250929"),
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}]
        )
        
        import json
        response_text = message.content[0].text
        
        # Try to parse JSON
        try:
            ai_tags = json.loads(response_text)
            return ai_tags
        except json.JSONDecodeError:
            return generate_tags_keyword_based(text)
            
    except Exception as e:
        print(f"AI tagging failed: {e}, using keyword-based tags")
        return generate_tags_keyword_based(text)


def generate_tags(text: str, use_ai: bool = False) -> Dict[str, Any]:
    """
    Main tagging function combining keyword and AI tagging
    
    Args:
        text: Text to analyze
        use_ai: Use AI enhancement (default: False for speed)
    
    Returns:
        Dictionary with tags and metadata
    """
    # Always get keyword tags
    keyword_tags = generate_tags_keyword_based(text)
    
    if use_ai:
        try:
            ai_tags = generate_tags_ai_enhanced(text)
            
            # Merge tags
            all_tags = list(set(keyword_tags["tags"] + ai_tags.get("tags", [])))
            
            return {
                "tags": all_tags,
                "detected_categories": keyword_tags["detected_categories"],
                "primary_theme": ai_tags.get("primary_theme", ""),
                "consciousness_level": ai_tags.get("consciousness_level", ""),
                "program_level": ai_tags.get("program_level", "beginner")
            }
        except Exception as e:
            print(f"AI enhancement failed: {e}")
            return keyword_tags
    
    return keyword_tags
