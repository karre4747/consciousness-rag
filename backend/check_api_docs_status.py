
import requests
import json

try:
    response = requests.get("http://localhost:8000/document-status")
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Total Documents: {data.get('total_documents')}")
        docs = data.get('documents', [])
        analyzed_count = sum(1 for d in docs if d.get('pass_3_status') == 'Complete')
        print(f"Analyzed Documents Count: {analyzed_count}")
        
        print("\n--- Sample Analyzed Documents ---")
        found = 0
        for d in docs:
            if d.get('pass_3_status') == 'Complete':
                print(f"Title: {d['title']}, Pass 3 Status: {d['pass_3_status']}")
                found += 1
                if found >= 5: break
                
        if found == 0:
            print("NO documents marked as 'Complete' for Pass 3.")
            
        print("\n--- Sample Pending Documents ---")
        found = 0
        for d in docs:
            if d.get('pass_3_status') != 'Complete':
                 print(f"Title: {d['title']}, Pass 3 Status: {d['pass_3_status']}")
                 found += 1
                 if found >= 5: break

except Exception as e:
    print(f"Error checking API: {e}")
