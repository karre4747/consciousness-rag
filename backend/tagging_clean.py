"""
Evolve Consciousness Engine - Keyword-Based Tagging System
Comprehensive tagging for consciousness, recovery, mysticism, quantum physics, and esoteric teachings
Based on expanded-tagging-v2.py from original handoff documents
Updated: December 22, 2025
"""

from typing import Dict, Any, List


def generate_tags(text: str) -> Dict[str, Any]:
    """
    Generate comprehensive consciousness and recovery tags using keyword matching.
    This is the original 305-line tagging system from the Evolve handoff documents.
    
    Returns a dictionary with all detected tags organized by category.
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
        "yogic_samadhi": ["samadhi", "raja yoga", "kundalini", "self-realization", "turiya"]
    }

    # === CONSCIOUSNESS-MATTER BRIDGES ===
    bridge_concepts = {
        "photon_consciousness": ["photon consciousness", "light as awareness", "biophoton field", "light body"],
        "chakra_sephiroth": ["chakra sephiroth", "energy center correspondence", "tree of life chakras"],
        "quantum_mind": ["quantum mind", "consciousness field", "observer creates reality", "quantum consciousness"],
        "meridian_nadi": ["meridian nadi", "energy channel correspondence", "chi prana", "subtle energy pathways"]
    }

    # === HEALING MODALITIES ===
    healing_keywords = {
        "energy_healing": ["reiki", "pranic", "therapeutic touch", "qi gong", "energy work"],
        "sound_healing": ["sound bath", "singing bowls", "tuning forks", "binaural beats", "chanting"],
        "crystal_healing": ["crystals", "gemstones", "quartz", "amethyst", "crystal grid"],
        "breathwork": ["pranayama", "holotropic", "wim hof", "breath of fire", "alternate nostril"],
        "meditation": ["mindfulness", "vipassana", "transcendental", "zen", "loving-kindness"],
        "bodywork": ["massage", "acupuncture", "chiropractic", "craniosacral", "myofascial"],
        "plant_medicine": ["ayahuasca", "psilocybin", "san pedro", "iboga", "kambo"]
    }

    # === SACRED GEOMETRY ===
    sacred_geometry = {
        "flower_of_life": ["flower of life", "seed of life", "fruit of life"],
        "metatron": ["metatron's cube", "metatron", "archangel"],
        "sri_yantra": ["sri yantra", "shri yantra", "sacred geometry"],
        "platonic_solids": ["tetrahedron", "cube", "octahedron", "dodecahedron", "icosahedron"],
        "merkaba": ["merkaba", "merkabah", "light body vehicle"],
        "torus": ["torus", "toroidal", "energy field"],
        "fibonacci": ["fibonacci", "golden ratio", "phi", "spiral"]
    }

    # === SUBTLE BODIES ===
    subtle_bodies = {
        "etheric": ["etheric body", "vital body", "chi body", "prana"],
        "emotional": ["emotional body", "astral body", "feeling body"],
        "mental": ["mental body", "thought body", "mind body"],
        "causal": ["causal body", "soul body", "karmic body"],
        "buddhic": ["buddhic body", "intuitive body", "christ consciousness"],
        "atmic": ["atmic body", "spiritual body", "divine body"]
    }

    # Helper function to check keywords
    def check_keywords(keyword_dict: Dict[str, List[str]], category_name: str):
        detected = []
        for key, keywords in keyword_dict.items():
            for keyword in keywords:
                if keyword in text_lower:
                    detected.append(key)
                    tags.append(f"{category_name}:{key}")
                    break
        if detected:
            detected_categories[category_name] = detected

    # Helper for nested dictionaries (like recovery_keywords)
    def check_nested_keywords(nested_dict: Dict[str, Dict[str, List[str]]], parent_category: str):
        for subcategory, keyword_dict in nested_dict.items():
            detected = []
            for key, keywords in keyword_dict.items():
                for keyword in keywords:
                    if keyword in text_lower:
                        detected.append(key)
                        tags.append(f"{subcategory}:{key}")
                        break
            if detected:
                detected_categories[subcategory] = detected

    # Run all keyword checks
    check_keywords(chakra_keywords, "chakras")
    check_keywords(meridian_keywords, "meridians")
    check_nested_keywords(recovery_keywords, "recovery")
    check_keywords(consciousness_keywords, "consciousness_level")
    check_keywords(esoteric_keywords, "traditions")
    check_keywords(esoteric_teachers, "teachers")
    check_keywords(quantum_keywords, "quantum")
    check_keywords(quantum_particles, "quantum_particles")
    check_keywords(universal_laws, "universal_laws")
    check_keywords(ascension_paths, "ascension_paths")
    check_keywords(bridge_concepts, "bridge_concepts")
    check_keywords(healing_keywords, "healing_modalities")
    check_keywords(sacred_geometry, "sacred_geometry")
    check_keywords(subtle_bodies, "subtle_bodies")

    # Return comprehensive tag structure
    return {
        "all_tags": tags,
        "detected_categories": detected_categories,
        **detected_categories  # Flatten for easier filtering
    }


# For backwards compatibility
def generate_tags_keyword_based(text: str) -> Dict[str, Any]:
    """Alias for generate_tags() for backwards compatibility."""
    return generate_tags(text)
