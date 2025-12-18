
import asyncio
import os
from dotenv import load_dotenv
load_dotenv(override=True)

from tagging import claude_second_pass_analysis

# Mock document structure as expected by claude_second_pass_analysis
mock_docs = [
    {
        "id": "doc1",
        "title": "Test Document 1",
        "text": "This is a test document about consciousness and quantum mechanics. It explores the relationship between the observer and the observed.",
        "tags": ["consciousness", "quantum"]
    }
]

def test_analysis():
    print("Testing claude_second_pass_analysis...")
    try:
        result = claude_second_pass_analysis(mock_docs, batch_size=1)
        print("Analysis Result:", result)
        
        if result.get('cross_document_themes'):
            print("SUCCESS: Themes found")
        else:
            print("FAILURE: No themes found")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_analysis()
