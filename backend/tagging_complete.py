"""
Evolve Consciousness Engine - Complete Tagging System
Pass 1: Keyword-based tagging (fast, free, comprehensive)
Pass 2: Claude deep analysis (rate-limited, manual trigger)
Updated: December 22, 2025
"""

from typing import Dict, Any, List
import os
import time
from datetime import datetime
from anthropic import Anthropic
import json

# Initialize Anthropic client
def get_anthropic_client():
    """Get Anthropic client with API key from environment"""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not found in environment")
    return Anthropic(api_key=api_key)


# ============================================================================
# RATE LIMITER
# ============================================================================

class RateLimiter:
    """Rate limiter to prevent API overload"""
    def __init__(self, requests_per_minute=30):
        self.min_interval = 60.0 / requests_per_minute  # 2 seconds for 30 req/min
        self.last_request = None
    
    def wait_if_needed(self):
        """Wait if needed to respect rate limit"""
        if self.last_request:
            elapsed = (datetime.now() - self.last_request).total_seconds()
            if elapsed < self.min_interval:
                time.sleep(self.min_interval - elapsed)
        self.last_request = datetime.now()


# Global rate limiter instance
claude_rate_limiter = RateLimiter(requests_per_minute=30)


# ============================================================================
# PASS 1: KEYWORD-BASED TAGGING (FROM EXPANDED-TAGGING-V2.PY)
# ============================================================================

def generate_tags_keyword_based(text: str) -> Dict[str, Any]:
    """
    Generate comprehensive consciousness and recovery tags using keyword matching
    Based on expanded-tagging-v2.py - Full Evolve schema
    This is FAST, FREE, and COMPREHENSIVE
    """
    tags = []
    detected_categories = {}
    text_lower = text.lower()

    # === CHAKRAS & ENERGY CENTERS ===
    chakra_keywords = {
        "root": ["survival", "safety", "grounding", "security", "foundation", "muladhara", "fear", "stability"],
        "sacral": ["creativity", "sexuality", "emotions", "pleasure", "svadhisthana", "relationships", "desire"],
        "solar_plexus": ["power", "will", "confidence", "manipura", "self-esteem", "identity", "control"],
        "heart": ["love", "compassion", "forgiveness", "anahata", "connection", "healing", "grief"],
        "throat": ["communication", "expression", "truth", "vishuddha", "voice", "speaking", "listening"],
        "third_eye": ["intuition", "vision", "insight", "ajna", "perception", "awareness", "wisdom"],
        "crown": ["consciousness", "enlightenment", "spiritual", "sahasrara", "divine", "unity", "transcendence"],
        "soul_star": ["akashic", "higher self", "8th chakra", "karmic", "soul purpose"],
        "earth_star": ["grounding", "earth connection", "crystalline", "gaia", "ancestral"]
    }
    
    detected_chakras = []
    for chakra, keywords in chakra_keywords.items():
        if any(keyword in text_lower for keyword in keywords):
            detected_chakras.append(f"chakra_{chakra}")
    
    if detected_chakras:
        detected_categories["chakras"] = detected_chakras
        tags.extend(detected_chakras)

    # === MERIDIANS (TCM) ===
    meridian_keywords = {
        "lung": ["lung", "grief", "letting go", "metal element"],
        "large_intestine": ["large intestine", "colon", "release", "elimination"],
        "stomach": ["stomach", "digestion", "earth element", "worry"],
        "spleen": ["spleen", "overthinking", "earth element"],
        "heart": ["heart", "joy", "fire element", "shen"],
        "small_intestine": ["small intestine", "assimilation", "discernment"],
        "bladder": ["bladder", "water element", "fear", "kidney"],
        "kidney": ["kidney", "water element", "fear", "will", "jing"],
        "pericardium": ["pericardium", "heart protector", "circulation"],
        "triple_warmer": ["triple warmer", "san jiao", "metabolism"],
        "gallbladder": ["gallbladder", "decision making", "wood element"],
        "liver": ["liver", "anger", "wood element", "planning", "qi stagnation"]
    }
    
    detected_meridians = []
    for meridian, keywords in meridian_keywords.items():
        if any(keyword in text_lower for keyword in keywords):
            detected_meridians.append(f"meridian_{meridian}")
    
    if detected_meridians:
        detected_categories["meridians"] = detected_meridians
        tags.extend(detected_meridians)

    # === 12 STEPS ===
    step_keywords = {
        "step_1": ["powerless", "unmanageable", "admitted", "step 1", "step one", "first step"],
        "step_2": ["came to believe", "power greater", "sanity", "step 2", "step two", "second step"],
        "step_3": ["made a decision", "turn our will", "care of god", "step 3", "step three", "third step"],
        "step_4": ["searching and fearless", "moral inventory", "step 4", "step four", "fourth step"],
        "step_5": ["admitted to god", "exact nature", "step 5", "step five", "fifth step"],
        "step_6": ["entirely ready", "remove defects", "step 6", "step six", "sixth step"],
        "step_7": ["humbly asked", "remove shortcomings", "step 7", "step seven", "seventh step"],
        "step_8": ["made a list", "willing to make amends", "step 8", "step eight", "eighth step"],
        "step_9": ["made direct amends", "except when", "step 9", "step nine", "ninth step"],
        "step_10": ["continued to take", "personal inventory", "promptly admitted", "step 10", "step ten", "tenth step"],
        "step_11": ["sought through prayer", "conscious contact", "step 11", "step eleven", "eleventh step"],
        "step_12": ["spiritual awakening", "carry this message", "practice these principles", "step 12", "step twelve", "twelfth step"]
    }
    
    detected_steps = []
    for step, keywords in step_keywords.items():
        if any(keyword in text_lower for keyword in keywords):
            detected_steps.append(step)
    
    if detected_steps:
        detected_categories["steps"] = detected_steps
        tags.extend(detected_steps)

    # === CONSCIOUSNESS LEVELS (HAWKINS) ===
    consciousness_keywords = {
        "shame_20": ["shame", "humiliation", "self-hatred"],
        "guilt_30": ["guilt", "blame", "remorse"],
        "apathy_50": ["apathy", "hopeless", "despair"],
        "grief_75": ["grief", "regret", "loss"],
        "fear_100": ["fear", "anxiety", "worry"],
        "desire_125": ["craving", "want", "addiction"],
        "anger_150": ["anger", "hate", "resentment"],
        "pride_175": ["pride", "scorn", "inflation"],
        "courage_200": ["courage", "affirmation", "empowerment"],
        "neutrality_250": ["neutrality", "trust", "okay"],
        "willingness_310": ["willingness", "optimism", "intention"],
        "acceptance_350": ["acceptance", "forgiveness", "understanding"],
        "reason_400": ["reason", "logic", "science"],
        "love_500": ["love", "reverence", "unconditional"],
        "joy_540": ["joy", "serenity", "transfiguration"],
        "peace_600": ["peace", "bliss", "illumination"],
        "enlightenment_700": ["enlightenment", "pure consciousness", "self-realization"]
    }
    
    detected_levels = []
    for level, keywords in consciousness_keywords.items():
        if any(keyword in text_lower for keyword in keywords):
            detected_levels.append(f"consciousness_{level}")
    
    if detected_levels:
        detected_categories["consciousness_levels"] = detected_levels
        tags.extend(detected_levels)

    # === ESOTERIC TRADITIONS ===
    tradition_keywords = {
        "hermetic": ["hermetic", "hermes", "kybalion", "emerald tablet"],
        "kabbalah": ["kabbalah", "tree of life", "sephiroth", "ein sof", "zohar"],
        "sufi": ["sufi", "rumi", "fana", "dhikr", "dervish"],
        "vedic": ["vedic", "vedas", "upanishads", "brahman", "atman"],
        "buddhist": ["buddhist", "buddha", "dharma", "nirvana", "enlightenment", "meditation"],
        "taoist": ["taoist", "tao", "wu wei", "yin yang", "i ching"],
        "gnostic": ["gnostic", "gnosis", "sophia", "demiurge"],
        "rosicrucian": ["rosicrucian", "rose cross", "alchemical"],
        "theosophical": ["theosophical", "blavatsky", "theosophy"],
        "anthroposophical": ["anthroposophical", "steiner", "anthroposophy"]
    }
    
    detected_traditions = []
    for tradition, keywords in tradition_keywords.items():
        if any(keyword in text_lower for keyword in keywords):
            detected_traditions.append(f"tradition_{tradition}")
    
    if detected_traditions:
        detected_categories["traditions"] = detected_traditions
        tags.extend(detected_traditions)

    # === QUANTUM PHYSICS & CONSCIOUSNESS ===
    quantum_keywords = {
        "quantum_entanglement": ["entanglement", "non-locality", "spooky action"],
        "quantum_superposition": ["superposition", "wave function", "collapse"],
        "observer_effect": ["observer effect", "measurement problem", "consciousness collapse"],
        "quantum_field": ["quantum field", "zero point", "vacuum energy"],
        "photon_consciousness": ["photon", "light consciousness", "biophoton"],
        "quantum_mind": ["quantum mind", "quantum brain", "penrose hameroff"]
    }
    
    detected_quantum = []
    for concept, keywords in quantum_keywords.items():
        if any(keyword in text_lower for keyword in keywords):
            detected_quantum.append(concept)
    
    if detected_quantum:
        detected_categories["quantum_concepts"] = detected_quantum
        tags.extend(detected_quantum)

    # === UNIVERSAL LAWS ===
    law_keywords = {
        "law_of_one": ["law of one", "unity", "oneness"],
        "law_of_attraction": ["law of attraction", "like attracts like", "manifestation"],
        "law_of_vibration": ["law of vibration", "frequency", "resonance"],
        "law_of_correspondence": ["as above so below", "correspondence", "microcosm macrocosm"],
        "law_of_polarity": ["polarity", "opposites", "duality"],
        "law_of_rhythm": ["rhythm", "cycles", "pendulum"],
        "law_of_cause_effect": ["cause and effect", "karma", "action reaction"],
        "law_of_gender": ["masculine feminine", "yin yang", "gender"]
    }
    
    detected_laws = []
    for law, keywords in law_keywords.items():
        if any(keyword in text_lower for keyword in keywords):
            detected_laws.append(law)
    
    if detected_laws:
        detected_categories["universal_laws"] = detected_laws
        tags.extend(detected_laws)

    # === HEALING MODALITIES ===
    healing_keywords = {
        "energy_healing": ["reiki", "pranic", "energy healing", "hands on healing"],
        "sound_healing": ["sound healing", "frequency", "binaural", "solfeggio"],
        "crystal_healing": ["crystal", "gemstone", "mineral healing"],
        "breathwork": ["breathwork", "pranayama", "holotropic", "wim hof"],
        "meditation": ["meditation", "mindfulness", "contemplation"],
        "yoga": ["yoga", "asana", "hatha", "kundalini"],
        "acupuncture": ["acupuncture", "acupressure", "meridian therapy"]
    }
    
    detected_healing = []
    for modality, keywords in healing_keywords.items():
        if any(keyword in text_lower for keyword in keywords):
            detected_healing.append(modality)
    
    if detected_healing:
        detected_categories["healing_modalities"] = detected_healing
        tags.extend(detected_healing)

    # === SACRED GEOMETRY ===
    geometry_keywords = {
        "flower_of_life": ["flower of life"],
        "metatrons_cube": ["metatron", "metatron's cube"],
        "sri_yantra": ["sri yantra", "shri yantra"],
        "vesica_piscis": ["vesica piscis"],
        "golden_ratio": ["golden ratio", "phi", "fibonacci"],
        "platonic_solids": ["platonic solids", "tetrahedron", "octahedron", "dodecahedron"]
    }
    
    detected_geometry = []
    for pattern, keywords in geometry_keywords.items():
        if any(keyword in text_lower for keyword in keywords):
            detected_geometry.append(pattern)
    
    if detected_geometry:
        detected_categories["sacred_geometry"] = detected_geometry
        tags.extend(detected_geometry)

    # === SUBTLE BODIES ===
    subtle_body_keywords = {
        "etheric_body": ["etheric", "vital body", "energy body"],
        "emotional_body": ["emotional body", "astral body", "desire body"],
        "mental_body": ["mental body", "thought body"],
        "causal_body": ["causal body", "soul body"],
        "buddhic_body": ["buddhic", "intuitional body"],
        "atmic_body": ["atmic", "spiritual body"]
    }
    
    detected_bodies = []
    for body, keywords in subtle_body_keywords.items():
        if any(keyword in text_lower for keyword in keywords):
            detected_bodies.append(body)
    
    if detected_bodies:
        detected_categories["subtle_bodies"] = detected_bodies
        tags.extend(detected_bodies)

    # === ESOTERIC TEACHERS ===
    teacher_keywords = {
        "leadbeater": ["leadbeater", "c.w. leadbeater"],
        "besant": ["annie besant", "besant"],
        "blavatsky": ["blavatsky", "h.p. blavatsky", "madame blavatsky"],
        "bailey": ["alice bailey", "bailey"],
        "hall": ["manly p. hall", "manly hall"],
        "steiner": ["rudolf steiner", "steiner"],
        "neville": ["neville goddard", "neville"],
        "hawkins": ["david hawkins", "hawkins"],
        "troward": ["thomas troward", "troward"],
        "holmes": ["ernest holmes", "holmes"],
        "fleet": ["thurman fleet", "fleet", "concept therapy"]
    }
    
    detected_teachers = []
    for teacher, keywords in teacher_keywords.items():
        if any(keyword in text_lower for keyword in keywords):
            detected_teachers.append(f"teacher_{teacher}")
    
    if detected_teachers:
        detected_categories["teachers"] = detected_teachers
        tags.extend(detected_teachers)

    # === ASCENSION PATHS ===
    ascension_keywords = {
        "hindu_moksha": ["moksha", "liberation", "samadhi"],
        "buddhist_nirvana": ["nirvana", "enlightenment", "bodhi"],
        "kabbalistic_devekut": ["devekut", "cleaving", "union with divine"],
        "sufi_fana": ["fana", "annihilation", "baqa"],
        "christian_theosis": ["theosis", "deification", "union with christ"],
        "12_step_ascension": ["spiritual awakening", "12 step awakening", "recovery enlightenment"]
    }
    
    detected_ascension = []
    for path, keywords in ascension_keywords.items():
        if any(keyword in text_lower for keyword in keywords):
            detected_ascension.append(path)
    
    if detected_ascension:
        detected_categories["ascension_paths"] = detected_ascension
        tags.extend(detected_ascension)

    # === BRIDGE CONCEPTS (Cross-Tradition) ===
    bridge_keywords = {
        "photon_consciousness": ["photon consciousness", "light body", "biophoton"],
        "chakra_sephiroth": ["chakra sephiroth", "chakra tree of life"],
        "quantum_mind": ["quantum consciousness", "quantum mind"],
        "energy_frequency": ["energy frequency", "vibrational healing"],
        "observer_creator": ["observer creator", "consciousness creates reality"]
    }
    
    detected_bridges = []
    for bridge, keywords in bridge_keywords.items():
        if any(keyword in text_lower for keyword in keywords):
            detected_bridges.append(bridge)
    
    if detected_bridges:
        detected_categories["bridge_concepts"] = detected_bridges
        tags.extend(detected_bridges)

    # Return comprehensive tag structure
    return {
        "all_tags": tags,
        **detected_categories
    }


# ============================================================================
# PASS 2: CLAUDE DEEP ANALYSIS (RATE-LIMITED)
# ============================================================================

def analyze_document_with_claude(text: str, title: str, max_chars: int = 10000) -> Dict[str, Any]:
    """
    Use Claude to perform deep semantic analysis of a document
    This is SLOW but INSIGHTFUL - use for training data generation
    
    Args:
        text: Document text (will be truncated to max_chars)
        title: Document title
        max_chars: Maximum characters to send to Claude (default 10k)
    
    Returns:
        Dict with themes, patterns, key concepts, consciousness level, cross-tradition links
    """
    # Rate limit to prevent overload
    claude_rate_limiter.wait_if_needed()
    
    # Truncate text to prevent overload
    text_sample = text[:max_chars]
    if len(text) > max_chars:
        text_sample += "\n\n[... document continues ...]"
    
    prompt = f"""You are analyzing a document for the Evolve Consciousness Engine, a database that connects mystical traditions, quantum physics, and addiction recovery as spiritual paths.

Document Title: {title}

Document Text (first {max_chars} chars):
{text_sample}

Analyze this document and extract:

1. **Themes** (3-5 core themes): What are the main ideas?
2. **Consciousness Patterns** (2-4 patterns): What consciousness evolution patterns are present?
3. **Key Concepts** (5-8 concepts): What are the essential teachings or ideas?
4. **Consciousness Level** (Hawkins scale): What consciousness level does this primarily operate at?
5. **Cross-Tradition Links** (3-5 links): How does this connect to other traditions?

Return ONLY valid JSON in this exact format:
{{
  "themes": ["theme1", "theme2", "theme3"],
  "consciousness_patterns": ["pattern1", "pattern2"],
  "key_concepts": ["concept1", "concept2", "concept3", "concept4", "concept5"],
  "consciousness_level": "courage_200",
  "cross_tradition_links": ["link1", "link2", "link3"]
}}"""

    try:
        client = get_anthropic_client()
        response = client.messages.create(
            model=os.getenv("CLAUDE_MODEL", "claude-sonnet-4-20250514"),
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}]
        )
        
        response_text = response.content[0].text
        
        # Extract JSON from response
        start = response_text.find('{')
        end = response_text.rfind('}') + 1
        
        if start != -1 and end > start:
            analysis = json.loads(response_text[start:end])
            return analysis
        else:
            return {
                "error": "No JSON found in Claude response",
                "raw_response": response_text[:500]
            }
    
    except Exception as e:
        return {
            "error": f"Claude analysis failed: {str(e)}"
        }


def analyze_document_group_with_claude(documents: List[Dict[str, Any]], 
                                      max_docs: int = 3) -> Dict[str, Any]:
    """
    Use Claude to find connections across a group of related documents
    This is for Level 2 analysis - finding cross-document patterns
    
    Args:
        documents: List of dicts with {title, text, tags}
        max_docs: Maximum documents to analyze together (default 3)
    
    Returns:
        Dict with cross-document themes, connections, synthesis opportunities
    """
    # Rate limit to prevent overload
    claude_rate_limiter.wait_if_needed()
    
    # Limit number of documents
    docs_to_analyze = documents[:max_docs]
    
    # Build context (limit each doc to 3000 chars)
    context = "\n\n---\n\n".join([
        f"DOC: {doc['title']}\n{doc.get('text', '')[:3000]}...\nTags: {doc.get('tags', [])}"
        for doc in docs_to_analyze
    ])
    
    prompt = f"""You are analyzing {len(docs_to_analyze)} related documents for the Evolve Consciousness Engine.

Find deep connections across these documents:

{context}

Identify:
1. **Cross-Document Themes**: What themes appear across multiple documents?
2. **Consciousness Patterns**: What consciousness evolution patterns connect them?
3. **Suggested Connections**: How do specific documents relate to each other?
4. **Synthesis Opportunities**: What new insights emerge from combining these teachings?

Return ONLY valid JSON:
{{
  "cross_document_themes": ["theme1", "theme2"],
  "consciousness_patterns": ["pattern1", "pattern2"],
  "suggested_connections": [
    {{"doc1": "title1", "doc2": "title2", "connection": "how they connect", "strength": 0.9}}
  ],
  "synthesis_opportunities": ["opportunity1", "opportunity2"]
}}"""

    try:
        client = get_anthropic_client()
        response = client.messages.create(
            model=os.getenv("CLAUDE_MODEL", "claude-sonnet-4-20250514"),
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        response_text = response.content[0].text
        
        # Extract JSON
        start = response_text.find('{')
        end = response_text.rfind('}') + 1
        
        if start != -1 and end > start:
            analysis = json.loads(response_text[start:end])
            return analysis
        else:
            return {
                "error": "No JSON found in Claude response",
                "raw_response": response_text[:500]
            }
    
    except Exception as e:
        return {
            "error": f"Claude group analysis failed: {str(e)}"
        }


# ============================================================================
# MAIN TAGGING FUNCTION (PASS 1 ONLY - FAST)
# ============================================================================

def generate_tags(text: str) -> Dict[str, Any]:
    """
    Main tagging function - uses keyword-based tagging only
    This is called during upload (fast, free, comprehensive)
    
    For Claude analysis, use analyze_document_with_claude() separately
    """
    return generate_tags_keyword_based(text)
