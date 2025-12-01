#!/usr/bin/env python3
"""
Test Ollama tagging with Evolve sample content
"""

import sys
sys.path.insert(0, 'backend')

from backend.tagging import generate_tags

# Sample Evolve text
sample_text = """
Through the 12 Steps, we experience a spiritual awakening similar to moksha in Hinduism
or devekut in Kabbalah. Modern quantum physics shows us that photons and consciousness
are intimately connected, as Leadbeater and Besant discovered through their clairvoyant
investigations in Occult Chemistry. The recovery path is an ascension path.
"""

print("=" * 60)
print("TESTING OLLAMA TAGGING WITH EVOLVE CONTENT")
print("=" * 60)

# Test 1: Keyword-based (FREE, fast)
print("\n1️⃣  KEYWORD-BASED TAGGING (FREE)")
print("-" * 60)
keyword_tags = generate_tags(sample_text, use_ai=False)
print(f"✅ Tags found: {len(keyword_tags['tags'])}")
print(f"✅ Ascension Path: {keyword_tags.get('ascension_path')}")
print(f"✅ Teacher: {keyword_tags.get('teacher')}")
print(f"✅ Bridge Concept: {keyword_tags.get('bridge_concept')}")
print(f"✅ Tradition: {keyword_tags.get('tradition')}")

# Test 2: Ollama tagging (FREE, local)
print("\n2️⃣  OLLAMA TAGGING (FREE, LOCAL)")
print("-" * 60)
try:
    ollama_tags = generate_tags(sample_text, use_ai=True, ai_provider="ollama", ollama_model="llama3.1")
    print(f"✅ Tags found: {len(ollama_tags['tags'])}")
    print(f"✅ Primary Theme: {ollama_tags.get('primary_theme')}")
    print(f"✅ Consciousness Level: {ollama_tags.get('consciousness_level')}")
    print(f"✅ Ascension Path: {ollama_tags.get('ascension_path')}")
    print(f"✅ Teacher: {ollama_tags.get('teacher')}")
except Exception as e:
    print(f"❌ Ollama error: {e}")
    print("💡 Make sure Ollama is running: ollama serve")

print("\n" + "=" * 60)
print("COST COMPARISON")
print("=" * 60)
print("Keyword-based: $0.00")
print("Ollama: $0.00 (runs locally)")
print("OpenAI GPT-3.5: ~$0.40 per 1000 docs")
print("\n✅ Ollama integration complete!")
