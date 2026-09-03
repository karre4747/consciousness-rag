#!/usr/bin/env python3
"""
Evolve Consciousness Engine - Two-Pass Tagging System
Pass 1: OpenAI GPT-4o-mini for fast initial tagging (during upload)
Pass 2: Claude for deep semantic analysis (background job)
Updated: November 30, 2025
"""

from typing import Dict, Any, List
import os
import logging
from openai import OpenAI
from anthropic import Anthropic

logger = logging.getLogger(__name__)

# Initialize clients
def get_openai_client():
    """Get OpenAI client with API key from environment"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment")
    return OpenAI(api_key=api_key, base_url="https://api.openai.com/v1")

def get_anthropic_client():
    """Get Anthropic client with API key from environment"""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not found in environment")
    return Anthropic(api_key=api_key)


def generate_tags_keyword_based(text: str) -> Dict[str, Any]:
    """
    Generate comprehensive consciousness and recovery tags using keyword matching
    Based on expanded-tagging-v2.py - Full Evolve schema
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

    # === MERIDIANS & ACUPUNCTURE POINTS ===
    meridian_keywords = {
        "lung": ["lung meridian", "grief", "letting go", "breath", "metal element", "po"],
        "large_intestine": ["large intestine", "release", "elimination", "colon"],
        "stomach": ["stomach meridian", "earth element", "worry", "digestion", "nourishment"],
        "spleen": ["spleen", "pancreas", "overthinking", "yi", "transformation"],
        "heart_meridian": ["heart meridian", "fire element", "shen", "joy", "love"],
        "small_intestine": ["small intestine", "absorption", "discernment", "separation"],
        "bladder": ["bladder meridian", "water element", "fear", "zhi", "willpower"],
        "kidney": ["kidney meridian", "jing", "essence", "fear", "wisdom", "ancestral qi"],
        "pericardium": ["pericardium", "heart protector", "circulation", "relationships"],
        "triple_warmer": ["triple warmer", "san jiao", "metabolism", "protection"],
        "gallbladder": ["gallbladder", "decision making", "wood element", "courage"],
        "liver": ["liver meridian", "hun", "anger", "vision", "planning", "detox"]
    }

    # === ADDICTION & RECOVERY SPECIFIC ===
    recovery_keywords = {
        "addiction_type": {
            "alcohol": ["alcohol", "drinking", "drunk", "sober", "alcoholism", "wine", "beer"],
            "drugs": ["drugs", "substance", "narcotics", "opioid", "cocaine", "meth"],
            "gambling": ["gambling", "betting", "casino", "lottery", "risk"],
            "sex": ["sex addiction", "porn", "compulsive sexual", "intimacy disorder"],
            "food": ["food addiction", "binge", "eating disorder", "bulimia", "anorexia"],
            "technology": ["internet addiction", "gaming", "social media", "phone addiction"],
            "codependency": ["codependent", "relationship addiction", "enabling", "boundaries"]
        },
        "recovery_stage": {
            "detox": ["detox", "withdrawal", "physical dependence", "cleansing"],
            "early_recovery": ["early recovery", "first 90 days", "pink cloud", "newcomer"],
            "sustained_recovery": ["long-term recovery", "maintenance", "ongoing recovery"],
            "relapse_prevention": ["relapse", "triggers", "cravings", "warning signs"],
            "spiritual_awakening": ["spiritual awakening", "transformation", "rebirth", "phoenix"]
        },
        "12_steps": {
            "step_1": ["powerlessness", "unmanageable", "admission", "surrender"],
            "step_2": ["came to believe", "higher power", "sanity", "restoration"],
            "step_3": ["decision", "turn over", "will", "care of god"],
            "step_4": ["moral inventory", "fearless", "searching", "resentments"],
            "step_5": ["admitted", "exact nature", "wrongs", "confession"],
            "step_6": ["ready", "defects", "character", "willingness"],
            "step_7": ["humbly", "remove", "shortcomings", "humility"],
            "step_8": ["amends list", "willing", "harmed", "persons"],
            "step_9": ["direct amends", "wherever possible", "injury"],
            "step_10": ["continued inventory", "promptly admitted", "daily"],
            "step_11": ["prayer", "meditation", "conscious contact", "knowledge"],
            "step_12": ["spiritual awakening", "carry message", "practice principles"]
        }
    }

    # === CONSCIOUSNESS LEVELS (Extended Hawkins Scale) ===
    consciousness_keywords = {
        "shame": ["shame", "humiliation", "worthless", "miserable", "20"],
        "guilt": ["guilt", "blame", "destruction", "remorse", "30"],
        "apathy": ["apathy", "despair", "hopeless", "giving up", "50"],
        "grief": ["grief", "regret", "sadness", "loss", "75"],
        "fear": ["fear", "anxiety", "worry", "danger", "100"],
        "desire": ["desire", "craving", "wanting", "addiction", "125"],
        "anger": ["anger", "hate", "aggression", "rage", "150"],
        "pride": ["pride", "scorn", "contempt", "inflation", "175"],
        "courage": ["courage", "affirmation", "empowerment", "200"],
        "neutrality": ["neutrality", "trust", "satisfaction", "250"],
        "willingness": ["willingness", "optimism", "hope", "310"],
        "acceptance": ["acceptance", "forgiveness", "harmony", "350"],
        "reason": ["reason", "understanding", "logic", "400"],
        "love": ["unconditional love", "reverence", "benevolence", "500"],
        "joy": ["joy", "serenity", "bliss", "compassion", "540"],
        "peace": ["peace", "tranquility", "transcendence", "600"],
        "enlightenment": ["enlightenment", "pure consciousness", "700-1000"]
    }

    # === ESOTERIC TRADITIONS ===
    esoteric_keywords = {
        "hermetic": ["hermetic", "hermes", "thoth", "emerald tablet", "as above", "kybalion"],
        "kabbalah": ["kabbalah", "sephiroth", "tree of life", "ein sof", "zohar", "merkabah"],
        "sufi": ["sufi", "whirling", "rumi", "dhikr", "fana", "mystical islam"],
        "gnostic": ["gnostic", "gnosis", "demiurge", "sophia", "pleroma", "archons"],
        "rosicrucian": ["rosicrucian", "rose cross", "alchemy", "christian mysticism", "fama fraternitatis"],
        "vedic": ["vedic", "vedas", "upanishads", "brahman", "atman", "sanskrit"],
        "buddhist": ["buddhist", "dharma", "sangha", "noble truths", "eightfold path", "nirvana"],
        "taoist": ["tao", "yin yang", "wu wei", "i ching", "qi gong", "five elements"],
        "shamanic": ["shaman", "ayahuasca", "plant medicine", "journey", "power animal", "soul retrieval"],
        "egyptian": ["egyptian", "isis", "osiris", "horus", "ankh", "pyramid", "book of dead"],
        "hindu": ["hindu", "hinduism", "yoga", "vedanta", "advaita", "bhagavad gita"],
        "christian_mysticism": ["christian mystic", "contemplative", "desert fathers", "teresa of avila", "john of the cross"],
        "essene": ["essene", "dead sea scrolls", "qumran", "nazarene", "gnostic christianity"]
    }

    # === ESOTERIC TEACHERS & PHILOSOPHERS ===
    esoteric_teachers = {
        "leadbeater": ["leadbeater", "charles leadbeater", "clairvoyance", "thought forms", "chakras leadbeater", "occult chemistry"],
        "besant": ["annie besant", "besant", "theosophy", "ancient wisdom", "occult chemistry"],
        "blavatsky": ["blavatsky", "helena blavatsky", "secret doctrine", "isis unveiled", "mahatmas", "theosophy"],
        "bailey": ["alice bailey", "djwhal khul", "tibetan master", "seven rays", "esoteric astrology"],
        "hall": ["manly p hall", "manly hall", "secret teachings", "philosophical research society"],
        "steiner": ["rudolf steiner", "anthroposophy", "spiritual science", "waldorf", "biodynamic"],
        "troward": ["thomas troward", "troward", "edinburgh lectures", "mental science", "creative process"],
        "holmes": ["ernest holmes", "science of mind", "religious science", "spiritual mind treatment"],
        "fleet": ["thurman fleet", "concept therapy", "rays of the dawn", "health imaging"],
        "goddard": ["neville goddard", "neville", "imagination creates reality", "feeling is the secret"],
        "murphy": ["joseph murphy", "power of subconscious", "cosmic mind"],
        "hawkins": ["david hawkins", "power vs force", "consciousness calibration", "letting go"],
        "dispenza": ["joe dispenza", "breaking the habit", "becoming supernatural", "neuroplasticity"],
        "lipton": ["bruce lipton", "biology of belief", "epigenetics", "cell membrane"],
        "eddy": ["mary baker eddy", "christian science", "science and health"],
        "hopkins": ["emma curtis hopkins", "high mysticism", "new thought"],
        "cady": ["h emilie cady", "lessons in truth", "unity"],
        "fillmore": ["myrtle fillmore", "charles fillmore", "unity", "affirmative prayer"],
        "fox": ["emmet fox", "sermon on the mount", "golden key", "mental equivalent"]
    }

    # === QUANTUM & SCIENTIFIC ===
    quantum_keywords = {
        "quantum_physics": ["quantum", "quantum mechanics", "quantum field", "quantum theory"],
        "field_theory": ["zero point", "unified field", "morphic field", "torsion field", "scalar", "akashic field"],
        "frequency": ["frequency", "vibration", "resonance", "harmonics", "cymatics", "solfeggio"],
        "neuroscience": ["neuroplasticity", "neurotransmitter", "dopamine", "serotonin", "gaba", "prefrontal"],
        "epigenetics": ["epigenetic", "gene expression", "methylation", "generational trauma"],
        "biofield": ["biofield", "aura", "electromagnetic", "biophoton", "kirlian"]
    }

    # === QUANTUM PARTICLES & CONCEPTS ===
    quantum_particles = {
        "photons": ["photon", "light particle", "electromagnetic radiation", "biophoton", "light body"],
        "bosons": ["boson", "higgs", "higgs boson", "force carrier", "gauge boson"],
        "fermions": ["fermion", "electron", "quark", "matter particle", "lepton"],
        "entanglement": ["quantum entanglement", "non-locality", "spooky action", "correlation", "bell's theorem"],
        "superposition": ["superposition", "multiple states", "wave function", "schrödinger"],
        "observer_effect": ["observer effect", "consciousness collapses", "measurement problem", "copenhagen interpretation"],
        "wave_particle": ["wave-particle duality", "double slit", "complementarity"],
        "zero_point": ["zero point energy", "vacuum energy", "quantum vacuum", "casimir effect"]
    }

    # === UNIVERSAL LAWS & PRINCIPLES ===
    universal_laws = {
        "law_of_one": ["law of one", "unity consciousness", "we are all one", "oneness"],
        "law_of_attraction": ["law of attraction", "manifestation", "like attracts", "magnetism"],
        "law_of_vibration": ["vibration", "frequency", "everything vibrates", "resonance"],
        "law_of_correspondence": ["as above so below", "microcosm", "macrocosm", "fractal"],
        "law_of_cause_effect": ["karma", "cause and effect", "action reaction", "consequences"],
        "law_of_rhythm": ["rhythm", "cycles", "pendulum", "seasons", "ebb and flow"],
        "law_of_polarity": ["polarity", "duality", "opposites", "light and dark", "balance"],
        "law_of_gender": ["masculine feminine", "creation", "generation", "yin yang"],
        "law_of_mind": ["law of mind", "thought creates", "mental causation", "mind over matter"]
    }

    # === COMPARATIVE MYSTICISM - ASCENSION PATHS ===
    ascension_paths = {
        "12_step_ascension": ["12 steps", "spiritual awakening", "higher power", "recovery path", "step work", "addiction ascension"],
        "hindu_moksha": ["moksha", "liberation", "samadhi", "self-realization", "atman-brahman", "jivanmukta"],
        "buddhist_nirvana": ["nirvana", "enlightenment", "bodhi", "cessation", "emptiness", "sunyata"],
        "kabbalistic_devekut": ["devekut", "cleaving to god", "tree of life ascent", "keter", "ain soph"],
        "sufi_fana": ["fana", "annihilation", "baqa", "union with beloved", "whirling", "dhikr"],
        "christian_theosis": ["theosis", "divinization", "union with christ", "mystical marriage", "dark night"],
        "rosicrucian_alchemy": ["spiritual alchemy", "transmutation", "philosopher's stone", "rose cross", "alchemical marriage"],
        "taoist_immortality": ["taoist immortality", "golden elixir", "inner alchemy", "neidan"],
        "yogic_samadhi": ["samadhi", "yoga", "raja yoga", "kundalini awakening", "siddhis"]
    }

    # === CONSCIOUSNESS-MATTER BRIDGES ===
    bridge_concepts = {
        "photon_consciousness": ["photon consciousness", "light as awareness", "biophoton field", "light body", "photon mind"],
        "chakra_sephiroth": ["chakra sephiroth", "energy center correspondence", "tree of life chakras"],
        "quantum_mind": ["quantum mind", "consciousness field", "observer creates reality", "quantum consciousness"],
        "meridian_nadi": ["meridian nadi", "energy channel correspondence", "chi prana", "subtle energy pathways"],
        "addiction_ascension": ["addiction as ascension", "recovery as spiritual path", "12 steps mystical path"],
        "neuroscience_mysticism": ["neuroscience mysticism", "brain and consciousness", "neural correlates"],
        "quantum_spirituality": ["quantum spirituality", "physics and consciousness", "science and mysticism"]
    }

    # === HEALING MODALITIES ===
    healing_keywords = {
        "energy_healing": ["reiki", "pranic", "quantum touch", "healing hands", "energy work"],
        "sound_healing": ["sound healing", "singing bowls", "tuning forks", "binaural", "mantras"],
        "crystal_healing": ["crystal", "gemstone", "quartz", "amethyst", "chakra stones"],
        "breathwork": ["breathwork", "pranayama", "holotropic", "wim hof", "breath of fire"],
        "meditation_type": ["vipassana", "transcendental", "zen", "mindfulness", "guided"],
        "bodywork": ["massage", "rolfing", "craniosacral", "somatic", "feldenkrais"],
        "plant_medicine": ["ayahuasca", "psilocybin", "san pedro", "iboga", "cannabis", "sacred plants"]
    }

    # === SACRED GEOMETRY ===
    sacred_geometry = {
        "patterns": ["flower of life", "metatron", "sri yantra", "golden ratio", "fibonacci", "vesica piscis"],
        "platonic_solids": ["tetrahedron", "cube", "octahedron", "dodecahedron", "icosahedron"],
        "symbols": ["ankh", "om", "yin yang", "pentagram", "hexagram", "cross", "spiral"]
    }

    # === SUBTLE BODIES ===
    subtle_bodies = {
        "etheric": ["etheric body", "vital body", "energy double", "prana body"],
        "emotional": ["emotional body", "astral body", "desire body", "feeling body"],
        "mental": ["mental body", "thought body", "lower mind", "concrete mind"],
        "causal": ["causal body", "higher mental", "abstract mind", "soul body"],
        "buddhic": ["buddhic body", "intuitive body", "christ consciousness", "unity body"],
        "atmic": ["atmic body", "spiritual will", "divine purpose", "monadic"]
    }

    # === ASTROLOGY ===
    astrology_keywords = {
        "planets": {
            "sun": ["sun sign", "solar return", "vitality", "ego", "identity", "solar energy"],
            "moon": ["moon sign", "lunar", "emotions", "subconscious", "instincts", "mother"],
            "mercury": ["mercury", "communication", "intellect", "thinking", "gemini ruler", "virgo ruler"],
            "venus": ["venus", "love", "beauty", "values", "relationships", "taurus ruler", "libra ruler"],
            "mars": ["mars", "action", "energy", "drive", "conflict", "aries ruler"],
            "jupiter": ["jupiter", "expansion", "growth", "abundance", "wisdom", "sagittarius ruler"],
            "saturn": ["saturn", "karma", "discipline", "structure", "time", "restriction", "capricorn ruler"],
            "uranus": ["uranus", "awakening", "change", "rebellion", "innovation", "aquarius ruler"],
            "neptune": ["neptune", "illusion", "spirituality", "dreams", "oneness", "pisces ruler"],
            "pluto": ["pluto", "transformation", "power", "rebirth", "intensity", "scorpio ruler"]
        },
        "zodiac_signs": {
            "aries": ["aries", "ram", "fire sign", "cardinal fire"],
            "taurus": ["taurus", "bull", "earth sign", "fixed earth"],
            "gemini": ["gemini", "twins", "air sign", "mutable air"],
            "cancer": ["cancer", "crab", "water sign", "cardinal water"],
            "leo": ["leo", "lion", "fire sign", "fixed fire"],
            "virgo": ["virgo", "virgin", "maiden", "earth sign", "mutable earth"],
            "libra": ["libra", "scales", "balance", "air sign", "cardinal air"],
            "scorpio": ["scorpio", "scorpion", "water sign", "fixed water"],
            "sagittarius": ["sagittarius", "archer", "centaur", "fire sign", "mutable fire"],
            "capricorn": ["capricorn", "goat", "sea goat", "earth sign", "cardinal earth"],
            "aquarius": ["aquarius", "water bearer", "air sign", "fixed air"],
            "pisces": ["pisces", "fish", "water sign", "mutable water"]
        }
    }

    # === PROCESS ALL CATEGORIES ===
    def check_keywords(category_dict, category_name):
        for key, keywords in category_dict.items():
            if any(kw in text_lower for kw in keywords):
                if category_name not in detected_categories:
                    detected_categories[category_name] = []
                detected_categories[category_name].append(key)
                tags.extend(keywords[:3])  # Add first 3 keywords as tags

    # Check all categories
    check_keywords(chakra_keywords, "chakras")
    check_keywords(meridian_keywords, "meridians")
    check_keywords(recovery_keywords["addiction_type"], "addiction_type")
    check_keywords(recovery_keywords["recovery_stage"], "recovery_stage")
    check_keywords(recovery_keywords["12_steps"], "twelve_steps")
    check_keywords(consciousness_keywords, "consciousness_level")
    check_keywords(esoteric_keywords, "traditions")
    check_keywords(esoteric_teachers, "teachers")
    check_keywords(quantum_keywords, "quantum_science")
    check_keywords(quantum_particles, "quantum_particles")
    check_keywords(universal_laws, "universal_laws")
    check_keywords(ascension_paths, "ascension_paths")
    check_keywords(bridge_concepts, "bridge_concepts")
    check_keywords(healing_keywords, "healing_modalities")
    check_keywords(sacred_geometry, "sacred_geometry")
    check_keywords(sacred_geometry, "sacred_geometry")
    check_keywords(subtle_bodies, "subtle_bodies")
    check_keywords(astrology_keywords["planets"], "planets")
    check_keywords(astrology_keywords["zodiac_signs"], "zodiac_signs")

    # === EMOTION DETECTION ===
    emotions = []
    emotion_keywords = {
        "fear": ["fear", "afraid", "anxiety", "panic", "terror", "worry"],
        "anger": ["anger", "rage", "fury", "irritation", "frustration", "resentment"],
        "sadness": ["sad", "grief", "sorrow", "depression", "melancholy", "despair"],
        "joy": ["joy", "happy", "elated", "bliss", "ecstatic", "euphoric"],
        "love": ["love", "compassion", "kindness", "affection", "care", "devotion"],
        "shame": ["shame", "humiliation", "embarrassment", "worthless", "inadequate"],
        "guilt": ["guilt", "remorse", "regret", "blame", "fault", "responsible"],
        "peace": ["peace", "calm", "serene", "tranquil", "centered", "balanced"]
    }

    for emotion, keywords in emotion_keywords.items():
        if any(kw in text_lower for kw in keywords):
            emotions.append(emotion)

    return {
        "tags": list(set(tags))[:50],  # Limit to 50 unique tags
        "detected_categories": detected_categories,
        "emotions": emotions,
        "primary_chakra": detected_categories.get("chakras", [""])[0] if detected_categories.get("chakras") else "",
        "consciousness_level": detected_categories.get("consciousness_level", ["neutrality"])[0] if detected_categories.get("consciousness_level") else "neutrality",
        "tradition": detected_categories.get("traditions", [""])[0] if detected_categories.get("traditions") else "",
        "teacher": detected_categories.get("teachers", [""])[0] if detected_categories.get("teachers") else "",
        "ascension_path": detected_categories.get("ascension_paths", [""])[0] if detected_categories.get("ascension_paths") else "",
        "bridge_concept": detected_categories.get("bridge_concepts", [""])[0] if detected_categories.get("bridge_concepts") else "",
        "recovery_focus": detected_categories.get("addiction_type", [""])[0] if detected_categories.get("addiction_type") else "",
        "healing_modality": detected_categories.get("healing_modalities", [""])[0] if detected_categories.get("healing_modalities") else "",
        "primary_planet": detected_categories.get("planets", [""])[0] if detected_categories.get("planets") else "",
        "zodiac_sign": detected_categories.get("zodiac_signs", [""])[0] if detected_categories.get("zodiac_signs") else ""
    }


def generate_tags_ollama(text: str, model: str = "llama3.3") -> Dict[str, Any]:
    """
    Use Ollama (local LLM) for FREE tagging with semantic understanding
    Requires Ollama running locally: brew install ollama && ollama pull llama3.3
    """
    import requests
    import json

    # Truncate to reasonable limit for local processing
    MAX_OLLAMA_CHARS = 50000
    text_to_analyze = text[:MAX_OLLAMA_CHARS] if len(text) > MAX_OLLAMA_CHARS else text

    prompt = f"""Analyze this consciousness/spiritual text and identify relevant tags.

Text:
{text_to_analyze}

Return ONLY valid JSON with these fields:
{{
  "tags": ["chakra_heart", "quantum_physics", "step_1", "photon_consciousness", "moksha", etc],
  "primary_theme": "one sentence summary",
  "consciousness_level": "shame|fear|courage|acceptance|love|peace|enlightenment"
}}

Categories: chakras, meridians, 12_steps, consciousness_levels (Hawkins scale), esoteric_traditions (hermetic/kabbalah/sufi/vedic/buddhist/taoist/gnostic/rosicrucian), esoteric_teachers (leadbeater/besant/blavatsky/bailey/steiner/goddard/hawkins/dispenza), quantum_physics, quantum_particles (photons/bosons/fermions/entanglement), ascension_paths (12_step_ascension/moksha/nirvana/devekut/fana/theosis), bridge_concepts (photon_consciousness/chakra_sephiroth/quantum_mind/addiction_ascension), universal_laws, healing_modalities, sacred_geometry, subtle_bodies"""

    try:
        # Call local Ollama API
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "num_predict": 300
                }
            },
            timeout=60
        )

        if response.status_code == 200:
            result = response.json()
            response_text = result.get("response", "")

            # Parse JSON response
            try:
                # Try to find JSON in response
                start = response_text.find('{')
                end = response_text.rfind('}') + 1
                if start != -1 and end > start:
                    ai_tags = json.loads(response_text[start:end])
                    return ai_tags
                else:
                    return generate_tags_keyword_based(text)
            except json.JSONDecodeError:
                return generate_tags_keyword_based(text)
        else:
            print(f"Ollama API error: {response.status_code}, using keyword-based tags")
            return generate_tags_keyword_based(text)

    except requests.exceptions.ConnectionError:
        print("Ollama not running. Start with: ollama serve")
        return generate_tags_keyword_based(text)
    except Exception as e:
        print(f"Ollama tagging failed: {e}, using keyword-based tags")
        return generate_tags_keyword_based(text)


async def generate_tags_openai(text: str, openai_client, max_tokens: int = 300, timeout: float = 15.0) -> Dict[str, Any]:
    """
    PASS 1: Use OpenAI GPT-4o-mini for fast, cheap initial tagging during upload
    This replaces the expensive Claude call with a very affordable model (~$0.15/1M tokens)
    
    Args:
        text: Text to analyze
        openai_client: OpenAI client instance (reused from main.py)
        max_tokens: Maximum tokens for response
        timeout: Timeout in seconds (default: 15.0)
    
    Returns:
        Dictionary with tags and metadata
    """
    import asyncio
    import json
    import random
    from openai import OpenAIError, RateLimitError, APITimeoutError, APIConnectionError

    # GPT-4o-mini context window: 128k tokens = ~500k chars
    # Setting a safe limit of 100k chars allows massive headroom
    MAX_OPENAI_CHARS = 100000
    text_to_analyze = text[:MAX_OPENAI_CHARS] if len(text) > MAX_OPENAI_CHARS else text

    prompt = f"""Analyze this consciousness/spiritual text and identify relevant tags.

Text:
{text_to_analyze}

Return ONLY valid JSON with these fields:
{{
  "tags": ["chakra_heart", "quantum_physics", "step_1", "photon_consciousness", "moksha", etc],
  "primary_theme": "one sentence summary",
  "consciousness_level": "shame|fear|courage|acceptance|love|peace|enlightenment"
}}

Categories: chakras, meridians, 12_steps, consciousness_levels (Hawkins scale), esoteric_traditions (hermetic/kabbalah/sufi/vedic/buddhist/taoist/gnostic/rosicrucian), esoteric_teachers (leadbeater/besant/blavatsky/bailey/steiner/goddard/hawkins/dispenza), quantum_physics, quantum_particles (photons/bosons/fermions/entanglement), ascension_paths (12_step_ascension/moksha/nirvana/devekut/fana/theosis), bridge_concepts (photon_consciousness/chakra_sephiroth/quantum_mind/addiction_ascension), universal_laws, healing_modalities, sacred_geometry, subtle_bodies, astrology (planets/zodiac_signs)"""

    max_retries = 3
    base_delay = 1
    max_delay = 30

    def _call_openai():
        """Synchronous OpenAI API call"""
        return openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=0.3
        )

    for attempt in range(max_retries):
        try:
            # Run blocking OpenAI call in thread pool with timeout
            response = await asyncio.wait_for(
                asyncio.to_thread(_call_openai),
                timeout=timeout
            )

            response_text = response.choices[0].message.content

            # Parse JSON response
            try:
                ai_tags = json.loads(response_text)
                return ai_tags
            except json.JSONDecodeError:
                # Fallback to keyword-based tags if JSON parsing fails
                return generate_tags_keyword_based(text)

        except asyncio.TimeoutError:
            if attempt == max_retries - 1:
                print(f"OpenAI tagging timed out after {max_retries} attempts, using keyword-based tags")
                return generate_tags_keyword_based(text)
            delay = min(base_delay * (2 ** attempt), max_delay)
            jitter = random.uniform(0, delay * 0.1)
            print(f"OpenAI timeout, retrying in {delay + jitter:.2f}s (attempt {attempt + 1}/{max_retries})")
            await asyncio.sleep(delay + jitter)

        except (RateLimitError, APIConnectionError) as e:
            # Retry on rate limits and connection errors
            if attempt == max_retries - 1:
                print(f"OpenAI rate limit/connection error after {max_retries} attempts: {e}, using keyword-based tags")
                return generate_tags_keyword_based(text)
            delay = min(base_delay * (2 ** attempt), max_delay)
            jitter = random.uniform(0, delay * 0.1)
            print(f"OpenAI rate limit/connection error, retrying in {delay + jitter:.2f}s (attempt {attempt + 1}/{max_retries})")
            await asyncio.sleep(delay + jitter)

        except OpenAIError as e:
            # Don't retry on other OpenAI errors (e.g., invalid API key, bad request)
            print(f"OpenAI error (not retrying): {e}, using keyword-based tags")
            return generate_tags_keyword_based(text)

        except Exception as e:
            # Unexpected errors - don't retry
            print(f"Unexpected error during OpenAI tagging: {e}, using keyword-based tags")
            return generate_tags_keyword_based(text)

    # Fallback if all retries exhausted
    return generate_tags_keyword_based(text)


async def generate_tags(text: str, use_ai: bool = False, ai_provider: str = "ollama", title: str = "", ollama_model: str = "llama3.3", openai_client=None) -> Dict[str, Any]:
    """
    Main tagging function combining keyword and AI tagging

    Args:
        text: Text to analyze
        use_ai: Use AI enhancement (default: False for speed and FREE)
        ai_provider: "ollama" (FREE, local) or "openai" (paid but faster) - default: "ollama"
        title: Document title (used for program_level detection in addiction content)
        ollama_model: Ollama model to use (default: "llama3.3")
        openai_client: OpenAI client instance (required if ai_provider="openai")

    Returns:
        Dictionary with tags and metadata

    Cost comparison:
        - use_ai=False: FREE (keyword-based only)
        - use_ai=True, ai_provider="ollama": FREE (runs locally)
        - use_ai=True, ai_provider="openai": ~$0.40 per 1000 docs
    """
    # Always get keyword tags
    keyword_tags = generate_tags_keyword_based(text)

    # Detect program_level from filename for addiction-specific content
    program_level = None
    if title:
        title_lower = title.lower()
        if title_lower.startswith("beginner"):
            program_level = "beginner"
        elif title_lower.startswith("intermediate"):
            program_level = "intermediate"
        elif title_lower.startswith("advanced"):
            program_level = "advanced"

    if use_ai:
        try:
            # Choose AI provider
            if ai_provider == "ollama":
                # Run synchronous Ollama call in a separate thread to avoid blocking the event loop
                import asyncio
                ai_tags = await asyncio.to_thread(generate_tags_ollama, text, model=ollama_model)
            elif ai_provider == "openai":
                if not openai_client:
                    raise ValueError("openai_client is required when ai_provider='openai'")
                ai_tags = await generate_tags_openai(text, openai_client)
            else:
                print(f"Unknown AI provider: {ai_provider}, using keyword-based tags")
                ai_tags = {}

            # Merge tags
            all_tags = list(set(keyword_tags["tags"] + ai_tags.get("tags", [])))

            result = {
                "tags": all_tags,
                "detected_categories": keyword_tags["detected_categories"],
                "primary_theme": ai_tags.get("primary_theme", ""),
                "consciousness_level": ai_tags.get("consciousness_level", keyword_tags.get("consciousness_level", "")),
                "emotions": keyword_tags.get("emotions", []),
                "primary_chakra": keyword_tags.get("primary_chakra", ""),
                "tradition": keyword_tags.get("tradition", ""),
                "teacher": keyword_tags.get("teacher", ""),
                "ascension_path": keyword_tags.get("ascension_path", ""),
                "bridge_concept": keyword_tags.get("bridge_concept", ""),
                "recovery_focus": keyword_tags.get("recovery_focus", ""),
                "healing_modality": keyword_tags.get("healing_modality", ""),
                "ai_provider": ai_provider,
                "ai_model": ollama_model if ai_provider == "ollama" else "gpt-4o-mini"
            }

            # Only add program_level if detected from filename
            if program_level:
                result["program_level"] = program_level

            return result
        except Exception as e:
            print(f"AI enhancement failed: {e}")
            # Add program_level to keyword tags if detected
            if program_level:
                keyword_tags["program_level"] = program_level
            return keyword_tags

    # Add program_level to keyword tags if detected
    if program_level:
        keyword_tags["program_level"] = program_level
    return keyword_tags



def repair_json_quotes(s: str) -> str:
    """Escape double quotes that appear inside JSON string values.

    Claude occasionally writes prose like: the "I" in the Fabric — inside a
    string value without escaping. Walk the text tracking string state; a
    closing quote is only accepted if the next non-space char is structural
    (: , } ]), otherwise the quote is literal content and gets escaped.
    Valid JSON passes through unchanged.
    """
    out = []
    in_str = False
    i = 0
    n = len(s)
    while i < n:
        c = s[i]
        if in_str:
            if c == '\\':
                out.append(s[i:i + 2]); i += 2; continue
            if c == '"':
                j = i + 1
                while j < n and s[j] in ' \t\r\n':
                    j += 1
                if j >= n or s[j] in ':,}]':
                    in_str = False
                    out.append(c)
                else:
                    out.append('\\"')
                i += 1; continue
            out.append(c); i += 1; continue
        if c == '"':
            in_str = True
        out.append(c); i += 1
    return ''.join(out)

def claude_second_pass_analysis(documents: List[Dict[str, Any]], batch_size: int = 5) -> Dict[str, Any]:
    """
    PASS 2: Claude analyzes ALL documents together to find deep connections
    Run this AFTER upload is complete, as a background job

    Args:
        documents: List of document dicts with {id, text, existing_tags}

    Returns:
        Dict with enhanced semantic connections and relationships
    """
    import json
    # Build context with full text (up to reasonable safety limit per doc to allow batching)
    MAX_CHARS_PER_DOC = 30000
    limited_docs = documents[:batch_size]
    context = "\n\n---\n\n".join([
        f"DOC {i+1} [{doc.get('id')}]:\n{doc.get('text', '')[:MAX_CHARS_PER_DOC]}...\nALL Tags: {doc.get('tags', [])}"
        for i, doc in enumerate(limited_docs)
    ])

    # Fetch already analyzed documents from the database to suggest connections to existing files
    existing_docs_context = ""
    try:
        import database
        all_db_docs = database.get_all_documents()
        analyzed_docs = []
        batch_titles = {d.get('id') for d in limited_docs}.union({d.get('title') for d in limited_docs})
        for d in all_db_docs:
            title = d.get("title", "")
            if d.get("status") == "analyzed" and d.get("analysis_results") and title not in batch_titles:
                try:
                    res = json.loads(d["analysis_results"])
                    themes = res.get("cross_document_themes", [])[:3]  # limit to top 3 themes to keep prompt slim
                    analyzed_docs.append(f'- "{title}" (Key Themes: {themes})')
                except Exception:
                    pass
        if analyzed_docs:
            existing_docs_context = "\n\nEXISTING REFERENCE LIBRARY (Already Analyzed in Database):\n" + "\n".join(analyzed_docs)
    except Exception as e:
        logger.error(f"Error fetching existing documents for reference context: {e}")

    prompt = f"""You are analyzing a consciousness and spiritual transformation database.

Your task is to analyze the documents provided in the DOCUMENTS section and return a valid JSON object.

CRITICAL REQUIREMENTS:
- Return ONLY a valid JSON object matching the exact schema below.
- "cross_document_themes": Identify between 5 to 7 most significant themes. Provide a detailed, context-rich paragraph for each theme.
- "consciousness_patterns": Identify between 5 to 7 consciousness patterns, explaining how they manifest across documents.
- "synthesis_opportunities": Identify between 5 to 7 synthesis opportunities, explaining how these teachings integrate.
- "suggested_connections": Suggest between 5 to 10 important connections. For each connection, provide a detailed 2 to 3 sentence explanation of the connection's nature and relevance.
- Ensure all double quotes inside JSON string values are properly escaped (e.g. use \\" for nested quotes).
- Do NOT include any trailing commas or unescaped newlines.
- In suggested_connections, doc_id and relates_to MUST contain the exact document titles as provided in the square brackets (e.g. "124685109-Quantum-Healing.pdf") or reference titles (e.g. "BHBY-CH-13.pdf") including their file extensions, numbers, and case sensitivity. Do not use shorthand index like "DOC 1".

DOCUMENTS TO ANALYZE:
{context}
{existing_docs_context}

Return JSON matching this schema:
{{
  "cross_document_themes": ["Detailed paragraph of theme 1", "Detailed paragraph of theme 2"],
  "consciousness_patterns": ["Detailed explanation of pattern 1", "Detailed explanation of pattern 2"],
  "suggested_connections": [
    {{"doc_id": "Exact Document Title 1", "relates_to": "Exact Document Title 2", "connection": "Detailed 2-3 sentence explanation of why they connect"}}
  ],
  "synthesis_opportunities": ["Detailed explanation of opportunity 1"]
}}

REMEMBER: Return ONLY the JSON object. Do not explain anything else. Do not violate this format!"""

    try:
        client = get_anthropic_client()
        message = client.messages.create(
            model=os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20241022"),
            # Sonnet 4.5 writes ~44k chars for a 5-doc batch; 8192 truncated mid-JSON.
            max_tokens=int(os.getenv("CLAUDE_ANALYSIS_MAX_TOKENS", "20000")),
            messages=[{"role": "user", "content": prompt}]
        )

        import json
        import re
        response_text = message.content[0].text
        if getattr(message, "stop_reason", None) == "max_tokens":
            logger.warning("Claude analysis response was truncated at max_tokens; JSON will likely fail to parse")

        # Extract JSON from response
        json_str = ""
        try:
            # Try to find JSON in response
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            if start != -1 and end > start:
                json_str = response_text[start:end]
                analysis = json.loads(json_str)
                return analysis
            else:
                logger.error(f"No JSON found in response. Raw response:\n{response_text}")
                return {"error": "No JSON found in response"}
        except json.JSONDecodeError as e:
            logger.warning(f"Initial JSON parse failed: {e}. Attempting recovery/cleaning...")
            try:
                # Clean trailing commas
                cleaned = re.sub(r',\s*([\]}])', r'\1', json_str)
                # Remove control chars (like raw newlines) in string values can be tricky,
                # but let's try parsing the cleaned JSON string first
                try:
                    analysis = json.loads(cleaned)
                    logger.info("JSON successfully parsed after cleaning trailing commas!")
                    return analysis
                except json.JSONDecodeError:
                    # Unescaped quotes inside string values are the other common failure
                    analysis = json.loads(repair_json_quotes(cleaned))
                    logger.info("JSON successfully parsed after escaping stray quotes!")
                    return analysis
            except Exception as e2:
                logger.error(f"JSON recovery failed. Error: {e2}\nRaw JSON string extracted:\n{json_str}\nFull Response text:\n{response_text}")
                return {"error": f"JSON parse error: {str(e)}"}

    except Exception as e:
        return {"error": f"Claude analysis failed: {str(e)}"}

async def generate_tags_batch_openai(texts: List[str], openai_client, max_tokens: int = 1500, timeout: float = 30.0) -> tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Batch processing for OpenAI tagging to reduce API calls.
    Processes up to 5-10 chunks in a single request.
    Returns: (results_list, usage_stats)
    """
    import asyncio
    import json
    import random
    from openai import OpenAIError, RateLimitError, APITimeoutError, APIConnectionError

    # GPT-4o-mini Pricing (Approximate)
    COST_INPUT_PER_1M = 0.15
    COST_OUTPUT_PER_1M = 0.60

    MAX_CHUNK_CHARS = 10000 
    MAX_TOTAL_CHARS = 100000 # Leave room for system prompt + output

    # Construct batch prompt with safety limits
    combined_text = ""
    for i, text in enumerate(texts):
        # Truncate individual chunk if needed
        clean_text = text[:MAX_CHUNK_CHARS] + "... (truncated)" if len(text) > MAX_CHUNK_CHARS else text
        
        # Check total accumulation
        if len(combined_text) + len(clean_text) > MAX_TOTAL_CHARS:
             print(f"Batch warning: Total text length {len(combined_text) + len(clean_text)} exceeds limit {MAX_TOTAL_CHARS}. Truncating batch content.")
             break
             
        combined_text += f"\n--- CHUNK {i+1} ---\n{clean_text}\n"

    prompt = f"""You are a tagging engine. Analyze the following {len(texts)} text chunks. 
For EACH chunk, identify relevant tags, themes, and consciousness levels.

CHUNKS TO ANALYZE:
{combined_text}

Return a valid JSON OBJECT with a key "results" which is a LIST of objects, one for each chunk in order:
{{
  "results": [
    {{
      "chunk_index": 1,
      "tags": ["tag1", "tag2"],
      "primary_theme": "theme description",
      "consciousness_level": "level"
    }},
    ...
  ]
}}

Categories to detect: chakras, recovery_principles, consciousness_levels, traditions, quantum_concepts.
"""

    max_retries = 5
    base_delay = 4
    max_delay = 60

    def _call_openai():
        return openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=0.3
        )

    # Helper for zero usage stats to prevent KeyErrors
    def make_zero_usage_stats():
        return {
            "total_cost": 0,
            "input_tokens": 0,
            "output_tokens": 0,
            "input_cost": 0,
            "output_cost": 0
        }

    for attempt in range(max_retries):
        try:
            response = await asyncio.wait_for(
                asyncio.to_thread(_call_openai),
                timeout=timeout
            )
            response_text = response.choices[0].message.content
            
            # Calculate Usage
            usage = response.usage
            input_tokens = usage.prompt_tokens
            output_tokens = usage.completion_tokens
            input_cost = (input_tokens / 1_000_000) * COST_INPUT_PER_1M
            output_cost = (output_tokens / 1_000_000) * COST_OUTPUT_PER_1M
            total_cost = input_cost + output_cost
            
            usage_stats = {
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "input_cost": input_cost,
                "output_cost": output_cost,
                "total_cost": total_cost 
            }

            try:
                # Clean up json if markdown block
                if "```json" in response_text:
                    response_text = response_text.split("```json")[1].split("```")[0].strip()
                elif "```" in response_text:
                    response_text = response_text.split("```")[1].split("```")[0].strip()

                data = json.loads(response_text)
                results = data.get("results", [])
                
                # Pad if missing
                while len(results) < len(texts):
                    results.append({})
                    
                return results, usage_stats
                
            except json.JSONDecodeError:
                # Fallback: return empty dicts to trigger keyword fallback
                return [{} for _ in texts], make_zero_usage_stats()

        except (RateLimitError, APIConnectionError) as e:
            if attempt == max_retries - 1: return [{} for _ in texts], make_zero_usage_stats()
            delay = min(base_delay * (2 ** attempt), max_delay)
            # Add jitter
            delay += random.uniform(0, 1)
            print(f"Batch OpenAI rate limit, retrying in {delay:.2f}s")
            await asyncio.sleep(delay)
            
        except Exception as e:
            print(f"Batch OpenAI error: {e}")
            return [{} for _ in texts], make_zero_usage_stats()

    return [{} for _ in texts], make_zero_usage_stats()

