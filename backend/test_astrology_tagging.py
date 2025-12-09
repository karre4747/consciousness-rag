
import sys
import os

# Add backend directory to path
sys.path.append("/Users/carriehuff/consciousness-RAG/consciousness-rag/backend")

from tagging import generate_tags_keyword_based

def test_astrology_tagging():
    # Test text containing astrology keywords
    text = "The Sun in Aries brings vitality and energy. Mercury retrograde affects communication. This is a time for Mars action."
    
    tags = generate_tags_keyword_based(text)
    
    print("Detected Categories:", tags["detected_categories"])
    print("Tags:", tags["tags"])
    
    # Verify planets
    planets = tags["detected_categories"].get("planets", [])
    if "sun" in planets and "mercury" in planets and "mars" in planets:
        print("✅ Planets detected correctly")
    else:
        print("❌ Planets detection failed")
        
    # Verify signs
    signs = tags["detected_categories"].get("zodiac_signs", [])
    if "aries" in signs:
        print("✅ Zodiac signs detected correctly")
    else:
        print("❌ Zodiac signs detection failed")
        
    return tags

if __name__ == "__main__":
    test_astrology_tagging()
