# Simplified Consciousness-RAG Deployment Guide

**Date:** December 22, 2025  
**Branch:** `simplified-clean-2024`  
**Status:** Ready for deployment

---

## What Changed

### Removed ❌
- SQLite database and sync overhead
- Multi-pass AI tagging (OpenAI Pass 2, Claude Pass 3)
- Ollama integration
- Background tasks (sync, re-tagging, analysis)
- Spending tracker and cost estimator
- Complex frontend features (Analysis, Tagging, Spending tabs)
- Full-document processing (unbounded memory)

### Kept ✅
- Comprehensive keyword-based tagging (305 lines from original handoff)
- Pinecone vector database
- OpenAI embeddings (text-embedding-3-large)
- Claude RAG queries (Sonnet 4.5)
- **1800-character chunks** (your correct size for long documents)
- Simple, clean architecture

### New Files
- `main_simplified.py` - Clean backend (400 lines vs. 1,896)
- `tagging_clean.py` - Keyword-only tagging (330 lines vs. 805)
- `index_simplified.html` - Simple frontend (400 lines vs. 2,781)

---

## Installation

### 1. Environment Setup

```bash
cd /home/ubuntu/consciousness-rag/backend

# Create virtual environment (if not exists)
python3.11 -m venv venv

# Activate
source venv/bin/activate

# Install dependencies
pip install fastapi uvicorn python-dotenv pinecone-client openai anthropic
```

### 2. Environment Variables

Create or update `.env` file:

```bash
# Required
PINECONE_API_KEY=your_pinecone_api_key
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key

# Optional (defaults are fine)
INDEX_NAME=consciousness-rag
CHUNK_SIZE=1800
CHUNK_OVERLAP=200
```

### 3. Replace Files

```bash
# Backup current files
cp main.py main_old.py
cp tagging.py tagging_old.py
cp static/index.html static/index_old.html

# Use simplified versions
cp main_simplified.py main.py
cp tagging_clean.py tagging.py
cp static/index_simplified.html static/index.html
```

---

## Testing

### 1. Start the Server

```bash
cd /home/ubuntu/consciousness-rag/backend
source venv/bin/activate
python main.py
```

Server will start on `http://localhost:8000`

### 2. Test Health Check

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "pinecone": "connected",
  "vector_count": 0,
  "chunk_size": 1800,
  "embedding_model": "text-embedding-3-large"
}
```

### 3. Test Upload

Create a test file `test_upload.json`:

```json
{
  "title": "Test Document - Step 1",
  "source": "AA Big Book",
  "text": "We admitted we were powerless over alcohol—that our lives had become unmanageable. This is the First Step of the 12 Steps. It requires complete honesty and surrender. The physical allergy and mental obsession make it impossible for the alcoholic to control their drinking. This is a spiritual awakening that begins with powerlessness."
}
```

Upload it:

```bash
curl -X POST http://localhost:8000/upload \
  -H "Content-Type: application/json" \
  -d @test_upload.json
```

Expected response:
```json
{
  "success": true,
  "title": "Test Document - Step 1",
  "chunks_processed": 1,
  "message": "Successfully uploaded 1 chunks"
}
```

### 4. Test Query

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is Step 1 about?",
    "top_k": 5
  }'
```

Expected response:
```json
{
  "answer": "Step 1 is about admitting powerlessness over alcohol...",
  "sources": [
    {
      "title": "Test Document - Step 1",
      "source": "AA Big Book",
      "score": 0.89,
      "tags": ["step_1:powerlessness", "step_1:unmanageable", ...]
    }
  ],
  "chunks_retrieved": 1
}
```

### 5. Test Frontend

Open browser to `http://localhost:8000`

You should see:
- 🧠 Evolve header
- 3 tabs: Upload, Query, Documents
- Clean, modern interface

Test:
1. Upload a document via the Upload tab
2. Query it via the Query tab
3. View it in the Documents tab

---

## Re-Indexing Your Content

Since you deleted the old Pinecone data and it never recovered, you'll need to re-upload your content with the new 1800-character chunk size.

### Option 1: Manual Upload via UI

1. Open `http://localhost:8000`
2. Go to Upload tab
3. Paste document text
4. Add title and source
5. Click Upload

### Option 2: Batch Upload Script

Create `batch_upload.py`:

```python
import requests
import os
import glob

API_URL = "http://localhost:8000/upload"

# Directory with your markdown files
CONTENT_DIR = "/path/to/your/content"

for filepath in glob.glob(f"{CONTENT_DIR}/**/*.md", recursive=True):
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()
    
    title = os.path.basename(filepath).replace('.md', '')
    source = os.path.dirname(filepath).split('/')[-1]
    
    print(f"Uploading: {title}")
    
    response = requests.post(API_URL, json={
        "title": title,
        "source": source,
        "text": text
    })
    
    if response.ok:
        data = response.json()
        print(f"  ✓ Success: {data['chunks_processed']} chunks")
    else:
        print(f"  ✗ Error: {response.text}")
```

Run it:

```bash
python batch_upload.py
```

---

## Deployment to Mac (Your Current Setup)

### Run as Background Service

Create `run_evolve.sh`:

```bash
#!/bin/bash
cd /home/ubuntu/consciousness-rag/backend
source venv/bin/activate
nohup python main.py > evolve.log 2>&1 &
echo $! > evolve.pid
echo "Evolve started on http://localhost:8000"
```

Make it executable:

```bash
chmod +x run_evolve.sh
```

Start:

```bash
./run_evolve.sh
```

Stop:

```bash
kill $(cat evolve.pid)
```

### Access from Other Devices

If you want to access from your phone/tablet on the same network:

1. Find your Mac's local IP:
   ```bash
   ifconfig | grep "inet " | grep -v 127.0.0.1
   ```

2. Update `main.py` to bind to all interfaces:
   ```python
   uvicorn.run(app, host="0.0.0.0", port=8000)
   ```

3. Access from other devices:
   ```
   http://YOUR_MAC_IP:8000
   ```

---

## Deployment to Cloud (Optional)

If you want to move back to cloud hosting (now that it's simplified):

### Digital Ocean Droplet (2GB RAM - Now Sufficient!)

1. **Create Droplet**
   - Ubuntu 22.04
   - 2GB RAM / 1 CPU ($12/month)
   - Choose region closest to you

2. **SSH and Setup**
   ```bash
   ssh root@your_droplet_ip
   
   # Install dependencies
   apt update
   apt install -y python3.11 python3.11-venv git
   
   # Clone repo
   git clone https://github.com/karre4747/consciousness-rag.git
   cd consciousness-rag
   git checkout simplified-clean-2024
   
   # Setup
   cd backend
   python3.11 -m venv venv
   source venv/bin/activate
   pip install fastapi uvicorn python-dotenv pinecone-client openai anthropic
   
   # Create .env file
   nano .env
   # (paste your API keys)
   ```

3. **Run with systemd**
   
   Create `/etc/systemd/system/evolve.service`:
   
   ```ini
   [Unit]
   Description=Evolve Consciousness Engine
   After=network.target
   
   [Service]
   Type=simple
   User=root
   WorkingDirectory=/root/consciousness-rag/backend
   Environment="PATH=/root/consciousness-rag/backend/venv/bin"
   ExecStart=/root/consciousness-rag/backend/venv/bin/python main.py
   Restart=always
   
   [Install]
   WantedBy=multi-user.target
   ```
   
   Enable and start:
   ```bash
   systemctl enable evolve
   systemctl start evolve
   systemctl status evolve
   ```

4. **Setup Nginx (Optional)**
   
   For HTTPS and domain name:
   ```bash
   apt install -y nginx certbot python3-certbot-nginx
   
   # Configure nginx
   nano /etc/nginx/sites-available/evolve
   ```
   
   Add:
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```
   
   Enable:
   ```bash
   ln -s /etc/nginx/sites-available/evolve /etc/nginx/sites-enabled/
   nginx -t
   systemctl restart nginx
   
   # Get SSL certificate
   certbot --nginx -d your-domain.com
   ```

---

## Performance Expectations

### With 1800-Character Chunks

| Metric | Expected Performance |
|--------|---------------------|
| **Upload time** | 3-5 seconds per document |
| **Query time** | 2-4 seconds |
| **Memory usage** | 300-500MB |
| **Startup time** | 5-10 seconds |
| **300-page book** | ~100-150 chunks (vs. 1500+ with 500-char) |

### Cost Estimates (Monthly)

| Service | Usage | Cost |
|---------|-------|------|
| **Pinecone** | Free tier (100k vectors) | $0 |
| **OpenAI Embeddings** | 1M tokens (~200 uploads) | $0.13 |
| **Claude Queries** | 1M input tokens (~500 queries) | $3.00 |
| **Total** | Light usage | **$3-10/month** |

With heavy usage (1000 uploads, 5000 queries):
- OpenAI: ~$0.65
- Claude: ~$30
- **Total: $30-50/month** (vs. $200-720 before)

---

## Troubleshooting

### Issue: "Pinecone not initialized"

**Solution:**
```bash
# Check .env file
cat .env | grep PINECONE

# Test Pinecone connection
python -c "from pinecone import Pinecone; pc = Pinecone(api_key='YOUR_KEY'); print(pc.list_indexes())"
```

### Issue: "Embedding generation failed"

**Solution:**
```bash
# Check OpenAI API key
python -c "from openai import OpenAI; client = OpenAI(); print(client.models.list())"
```

### Issue: "Claude query failed"

**Solution:**
```bash
# Check Anthropic API key
python -c "from anthropic import Anthropic; client = Anthropic(); print('OK')"
```

### Issue: Slow queries

**Possible causes:**
1. Too many chunks retrieved (reduce `top_k`)
2. Large context sent to Claude (normal, 2-4s is expected)
3. Network latency to APIs

### Issue: Out of memory

**This shouldn't happen with 1800-char chunks, but if it does:**
1. Reduce `CHUNK_SIZE` to 1200
2. Reduce `top_k` in queries
3. Check for memory leaks (restart server)

---

## Monitoring

### Check Server Status

```bash
# Is it running?
ps aux | grep "python main.py"

# Check logs
tail -f evolve.log

# Check memory usage
ps aux | grep python | awk '{print $6}'
```

### Check Pinecone Stats

```bash
curl http://localhost:8000/stats
```

### Check API Usage

- **OpenAI:** https://platform.openai.com/usage
- **Anthropic:** https://console.anthropic.com/settings/usage
- **Pinecone:** https://app.pinecone.io/

---

## Next Steps

1. ✅ Test the simplified system locally
2. ✅ Re-upload your content with 1800-char chunks
3. ✅ Verify tagging is working (check Documents tab)
4. ✅ Test cross-tradition queries
5. ✅ Deploy to production (Mac or cloud)
6. ✅ Monitor performance and costs

---

## Rollback Plan

If you need to go back to the old version:

```bash
# Restore old files
cp main_old.py main.py
cp tagging_old.py tagging.py
cp static/index_old.html static/index.html

# Restart server
pkill -f "python main.py"
python main.py
```

---

## Support

If you encounter issues:

1. Check the logs: `tail -f evolve.log`
2. Test each component individually (health, upload, query)
3. Verify API keys are valid
4. Check Pinecone index exists and is ready

---

**The simplified system is ready to deploy! 🚀**

This version preserves your original vision (comprehensive cross-tradition tagging) while removing all the bloat that was added later. It should run smoothly on your Mac M1 Max and be fast, reliable, and affordable.
