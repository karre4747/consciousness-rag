#!/usr/bin/env python3
"""
Evolve Consciousness Engine - Two-Pass Tagging System
Pass 1: OpenAI GPT-4o-mini for fast initial tagging (during upload)
Pass 2: Claude for deep semantic analysis (background job)
Updated: November 30, 2025
"""

from typing import Dict, Any, List
import os
from openai import OpenAI
from anthropic import Anthropic

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


