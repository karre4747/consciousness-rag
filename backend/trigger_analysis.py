
import urllib.request
import urllib.error
import json
import sqlite3

def trigger_analysis():
    # 1. Get pending titles from DB
    print("🔵 Connecting to database...")
    conn = sqlite3.connect('consciousness.db')
    cursor = conn.cursor()
    # Get everything that isn't analyzed
    cursor.execute("SELECT title FROM documents WHERE status != 'analyzed'")
    rows = cursor.fetchall()
    titles = [r[0] for r in rows]
    conn.close()

    if not titles:
        print("✅ No pending documents found! System is clear.")
        return

    print(f"📋 Found {len(titles)} pending documents.")
    print("🚀 Triggering 'Analyze Selected' via API (Bypassing UI)...")

    url = "http://localhost:8001/analyze-documents"
    payload = {
        "analysis_type": "selected",
        "selected_titles": titles[:100],  # Explicitly respect limit
        "limit": 100
    }

    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})

    try:
        with urllib.request.urlopen(req, timeout=300) as response:
            result = json.loads(response.read().decode('utf-8'))
            print(f"✅ Success! API Response: {result['status']}")
            print(f"📊 Processed: {result.get('documents_analyzed', 'Unknown')}")
    except urllib.error.HTTPError as e:
        print(f"❌ HTTP Error: {e.code} - {e.reason}")
        print(e.read().decode())
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    trigger_analysis()
