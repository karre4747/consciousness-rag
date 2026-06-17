#!/usr/bin/env python3
import sys
import os

# Align python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents import RecoveryAgent, MetaphysicsAgent, ScienceAgent, TherapyAgent, SynthesisAgent, SponsorAgent

def test_query(agent_instance, query_text):
    print("\n" + "="*80)
    print(f"🤖 TESTING AGENT: {agent_instance.name.upper()} (Collection: {agent_instance.collection_name})")
    print(f"❓ QUERY: '{query_text}'")
    print("="*80)
    
    result = agent_instance.query(query_text, top_k=3)
    
    if result["status"] == "success":
        print(f"\n💬 ANSWER:\n{result['answer']}")
        print(f"\n📂 CHUNKS RETRIEVED: {len(result['citations'])}")
        for i, c in enumerate(result['citations'], 1):
            print(f"  {i}. {c['title']} (score: {c['score']:.4f})")
    else:
        print(f"\n❌ FAILED: {result['answer']}")
    print("="*80 + "\n")

def main():
    print("🚀 Starting end-to-end agent system tests...")
    
    # 1. Recovery Agent (Addiction Recovery)
    recovery_agent = RecoveryAgent()
    test_query(recovery_agent, "What is Step 1 powerlessness about?")
    
    # 2. Sponsor Agent (Recovery Sponsorship)
    sponsor_agent = SponsorAgent()
    test_query(sponsor_agent, "I'm feeling like giving up and turning back. How do I handle this?")
    
    # 3. Metaphysics Agent (Esoteric Wisdom)
    metaphysics_agent = MetaphysicsAgent()
    test_query(metaphysics_agent, "What is the subconscious mind's role in transformation?")
    
    # 4. Science Agent (Quantum & Neuroscience)
    science_agent = ScienceAgent()
    test_query(science_agent, "Explain how neuroplasticity works in the brain.")
    
    # 5. Synthesis Agent (Cross-Domain Bridge)
    synthesis_agent = SynthesisAgent()
    test_query(synthesis_agent, "How does the act of surrender in Step 3 relate to quantum physics?")

if __name__ == "__main__":
    main()
