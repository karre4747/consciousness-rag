import requests
import time

BASE_URL = "http://localhost:8001"

def test_upload():
    print(f"Testing upload against {BASE_URL}...")
    
    # Check if server is up
    try:
        resp = requests.get(f"{BASE_URL}/api")
        print(f"Server Status: {resp.status_code} - {resp.json()}")
    except Exception as e:
        print(f"Server not reachable: {e}")
        return

    # Payload
    payload = {
        "title": "Test Document Alpha",
        "text": "This is a test document about consciousness and quantum physics. It mentions chakras and healing.",
        "source": "automated_test",
        "use_ai_tagging": False 
    }
    
    try:
        start = time.time()
        print("Sending upload request...")
        resp = requests.post(f"{BASE_URL}/upload", json=payload, timeout=30)
        print(f"Upload Response ({time.time() - start:.2f}s): {resp.status_code}")
        print(resp.text)
        if resp.status_code == 200:
            print("\nChecking /document-status...")
            time.sleep(1)
            status_resp = requests.get(f"{BASE_URL}/document-status")
            print(f"Status Response: {status_resp.status_code}")
            docs = status_resp.json().get("documents", [])
            found = any(d['title'] == "Test Document Alpha" for d in docs)
            print(f"Document found in status list: {found}")
            print("Documents list:", docs)
            
    except Exception as e:
        print(f"Test failed: {e}")

if __name__ == "__main__":
    test_upload()
