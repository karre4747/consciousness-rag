"""
Known author/work map for the consciousness library inventory.

Filenames in this corpus are often scrape artifacts, truncated, or personal
shorthand (BHBY, POSM). Matching them here is far more reliable than asking a
model to guess from a filename, so this map runs BEFORE the model pass and its
answers win.

Keys are matched case-insensitively against the filename.
"""

# Personal shorthand -> canonical work. These are the ones no model can infer.
SHORTHAND = {
    "bhby": ("Joe Dispenza", "Breaking the Habit of Being Yourself", "book"),
    "posm": ("Joseph Murphy", "The Power of the Subconscious Mind", "book"),
}

# Recurring authors in this library, matched by surname or common misspelling.
# "murphey" is a frequent typo in these filenames and must map to Murphy.
AUTHOR_PATTERNS = {
    "dispenza": "Joe Dispenza",
    "murphey": "Joseph Murphy",
    "murphy": "Joseph Murphy",
    "hawkins": "David R. Hawkins",
    "proctor": "Bob Proctor",
    "goddard": "Neville Goddard",
    "lipton": "Bruce Lipton",
    "blavatsky": "H.P. Blavatsky",
    "leadbeater": "C.W. Leadbeater",
    "besant": "Annie Besant",
    "steiner": "Rudolf Steiner",
    "hall": "Manly P. Hall",
    "goldsmith": "Joel S. Goldsmith",
    "goleman": "Daniel Goleman",
    "van der kolk": "Bessel van der Kolk",
    "mate": "Gabor Mate",
    "tolle": "Eckhart Tolle",
    # Concept Therapy. "CT" appears as a filename prefix (CTHandbook,
    # CTinAction) and no model infers Fleet from it.
    "fleet": "Thurman Fleet",
    "cthandbook": "Thurman Fleet",
    "ctinaction": "Thurman Fleet",
    "concept therapy": "Thurman Fleet",
    "rays of the dawn": "Thurman Fleet",
}

# Cross-framework parallels that no keyword or embedding will surface on its
# own, because neither body of literature uses the other's vocabulary.
# Recorded here so ingestion can write them into metadata.
FRAMEWORK_LINKS = {
    "thurman fleet": [
        "12-step-fourth-step",
        "character-defects-to-opposing-assets",
        "law-of-body-mind-soul",
        "ascension-path",  # Fleet's microorganism->human creation arc
    ],
}

# The library's central thesis: several traditions describe the SAME ascent
# in different vocabularies. None of these texts cite each other, and none
# share keywords, so no amount of search finds these links on its own. They
# are asserted here so ingestion can write them into metadata and the agent
# personas can reason across them.
#
# The shared spine, root -> crown:
#   chakra system   (yoga: muladhara -> sahasrara)
#   12 Steps        (admission -> spiritual awakening)
#   Fleet           (first vibration -> matter -> microorganism -> human)
#
# Karre is still adding sacred geometry, CRM therapy (eye positions /
# pineal activation) and astrology; revisit this map as those land.
ASCENSION_PATH = [
    {"stage": 1, "chakra": "root", "steps": [1],
     "theme": "survival, admission of powerlessness, first vibration/matter"},
    {"stage": 2, "chakra": "sacral", "steps": [2],
     "theme": "desire, coming to believe, emergence of life"},
    {"stage": 3, "chakra": "solar_plexus", "steps": [3],
     "theme": "will, turning it over, individuation"},
    {"stage": 4, "chakra": "heart", "steps": [4, 5],
     "theme": "inventory, defects to opposing assets, self-honesty"},
    {"stage": 5, "chakra": "throat", "steps": [6, 7, 8, 9],
     "theme": "expression, amends, readiness to change"},
    {"stage": 6, "chakra": "third_eye", "steps": [10, 11],
     "theme": "insight, meditation, pineal activation, CRM eye positions"},
    {"stage": 7, "chakra": "crown", "steps": [12],
     "theme": "spiritual awakening, remembering, service"},
]

# Collection routing by topic keyword. First match wins, so the more specific
# clinical terms are checked before the broad spiritual ones.
COLLECTION_PATTERNS = [
    ("addiction_recovery", [
        "addiction", "recovery", "sober", "sobriety", "12-step", "12 step",
        "twelve step", "step-", "aa-", "na-", "relapse", "substance",
        "alcohol", "codepend", "gambling", "big book", "naikan",
    ]),
    ("healing_modalities", [
        "cbt", "dbt", "emdr", "ifs", "somatic", "trauma", "therapy",
        "therapeutic", "attachment", "polyvagal", "inner child", "shadow work",
        "reiki", "breathwork", "worksheet", "grief", "anxiety", "depression",
    ]),
    ("science_bridge", [
        "quantum", "physics", "neuro", "brain", "epigenetic", "biology",
        "biophoton", "neuroplasticity", "cognitive", "psychology", "research",
        "study", "clinical",
    ]),
    ("metaphysics", [
        "metaphys", "hermetic", "kabbal", "vedic", "buddh", "hindu", "yoga",
        "zen", "kundalini", "chakra", "meditation", "mystic", "esoteric",
        "theosoph", "consciousness", "spiritual", "manifest", "subconscious",
        "astrology", "tarot", "akashic", "ascension",
        # New Thought / mindset vocabulary. Proctor, Murphy and Goddard sit
        # here; without these their work matches no collection at all.
        "paradigm", "mindset", "belief", "affirmation", "law of attraction",
        "prosperity", "abundance", "self-image", "autosuggestion",
        "new thought", "visualization", "intention",
    ]),
]

# Filenames/folders indicating Karre's OWN created content rather than source
# material. These are kept in a separate collection so the system never cites
# her work back to her as an independent source.
OWN_CONTENT_PATTERNS = [
    "breaking free", "breaking-free", "neuro recovery", "neurorecovery",
    "neuro-recovery", "comprehensive package", "complete_final_package",
    "wisdom path", "dreamweaver", "90-day", "90 day", "addiction series",
    "content load", "curriculum", "module", "week 1", "week 2", "week-1",
    "week-2", "evening review", "fred",  # Fred = a named client packet
]

# Karre's rule: worksheets SHE built are about the 12 Steps / addiction;
# worksheets about anything else were purchased from psychology-content
# platforms and are legitimate source material. So a worksheet is only
# "own content" when it also carries recovery subject matter.
RECOVERY_WORKSHEET_TERMS = [
    "step 1", "step 2", "step 3", "step 4", "step one", "step two",
    "step three", "step four", "step_1", "step_2", "step_3", "step_4",
    "12 step", "12-step", "twelve step", "inventory", "addiction",
    "recovery", "sober", "sobriety", "relapse", "sponsor",
]


# Material from Karre's other business interests that must never enter the
# consciousness library. Real-estate and creative-finance documents share a
# drive with the source material and otherwise slip through on generic words
# like "study guide" or "case study".
EXCLUDE_PATTERNS = [
    "subto", "sub-to", "sub to ", "creative financ", "seller financ",
    "wholesal", "real estate", "foreclos", "lease option", "land contract",
    "tax lien", "escrow", "deal case study", "cost summary", "laptop list",
    "auction list", "offering ",
    "katie-j", "katie j",  # named client notes, not source material
    # Records from Karre's former electronics-recycling company. These match
    # library vocabulary by coincidence -- chemical safety sheets contain
    # "alcohol", warehouse records contain "inventory" -- so they must be
    # excluded by name rather than by topic.
    "isopropyl", "swan 70", "clean product", "inbound inventory",
    "safety data sheet", "msds", "voluntary withdrawal",
]


def is_excluded(path: str) -> bool:
    """True for documents that must be kept out of the library entirely."""
    import os
    import re

    low = path.lower()
    if any(p in low for p in EXCLUDE_PATTERNS):
        return True

    # "Deal" as a standalone word marks real-estate material, but must not
    # catch words that merely contain it ("dealing", "idealism").
    name = os.path.splitext(os.path.basename(low))[0]
    if re.search(r"\bdeal\b", name):
        return True

    return False


def is_own_worksheet(path: str) -> bool:
    """True for worksheets on recovery topics, which Karre authored herself."""
    low = path.lower()
    if "worksheet" not in low and "workshop" not in low:
        return False
    return any(t in low for t in RECOVERY_WORKSHEET_TERMS)


def match_shorthand(filename: str):
    """Return (author, work, doc_type) if a shorthand code is present."""
    low = filename.lower()
    for code, (author, work, doc_type) in SHORTHAND.items():
        if code in low:
            return author, work, doc_type
    return None, None, None


def match_author(filename: str):
    """Return a canonical author name if a known surname appears."""
    low = filename.lower()
    for pattern, author in AUTHOR_PATTERNS.items():
        if pattern in low:
            return author
    return None


def match_collection(text: str):
    """Return the first collection whose keywords appear in the text."""
    low = text.lower()
    for collection, keywords in COLLECTION_PATTERNS:
        if any(k in low for k in keywords):
            return collection
    return None


def is_own_content(path: str):
    """True if the path looks like Karre's own created material."""
    low = path.lower()
    return any(p in low for p in OWN_CONTENT_PATTERNS)
