# Evolve Consciousness Engine - Troubleshooting Guide

**Version:** 1.0.0
**Last Updated:** November 30, 2025

Complete guide for diagnosing and fixing common issues.

---

## Table of Contents

- [Quick Diagnostics](#quick-diagnostics)
- [Upload Issues](#upload-issues)
- [Query Issues](#query-issues)
- [Server Issues](#server-issues)
- [Connection Issues](#connection-issues)
- [MCP Server Issues](#mcp-server-issues)
- [Performance Issues](#performance-issues)
- [Data Issues](#data-issues)
- [Cost & Spending Issues](#cost--spending-issues)
- [Debug Procedures](#debug-procedures)
- [Log Files](#log-files)
- [When to Restart](#when-to-restart)

---

## Quick Diagnostics

### Is the server running?

```bash
curl http://146.190.169.226:8000/health
```

**Expected:**
```json
{
  "status": "healthy",
  "pinecone": {"connected": true, "total_vectors": 1247},
  "openai": {"connected": true},
  "anthropic": {"connected": true}
}
```

**If it fails:**
- Server is down → See [Server Not Starting](#server-not-starting)
- Connection refused → Check SSH tunnel or network
- Timeout → Server overloaded or network issue

### Are services connected?

```bash
# Check individual services
curl http://146.190.169.226:8000/api
```

**Expected:**
```json
{
  "status": "Evolve Consciousness Engine Online",
  "version": "1.0.0",
  "services": {
    "pinecone": true,
    "openai": true,
    "anthropic": true
  }
}
```

**If any service is `false`:**
- Pinecone: Check API key, index name
- OpenAI: Check API key, billing status
- Anthropic: Check API key

### Can you upload?

```bash
curl -X POST http://146.190.169.226:8000/upload \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Test document content",
    "title": "Test Document"
  }'
```

**Expected:**
```json
{
  "status": "success",
  "chunks_created": 1,
  "vectors_uploaded": 1
}
```

### Can you query?

```bash
curl -X POST http://146.190.169.226:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is consciousness?",
    "top_k": 3
  }'
```

**Expected:**
```json
{
  "answer": "...",
  "sources": [...],
  "metadata": {"matches_found": 3}
}
```

---

## Upload Issues

### Upload Fails with "text field is required"

**Error:**
```json
{
  "detail": "Upload failed: text field is required"
}
```

**Cause:** Missing or empty `text` field in request

**Solution:**
```python
# Bad
data = {"title": "My Doc"}  # Missing text

# Good
data = {
    "text": "Document content here...",
    "title": "My Doc"
}
```

---

### Upload Times Out After 120 Seconds

**Error:**
```
requests.exceptions.ReadTimeout: HTTPSConnectionPool(...): Read timed out. (read timeout=120)
```

**Causes:**
1. Document is too large (>500KB)
2. AI tagging is enabled and slow
3. Server is overloaded
4. Network connection is slow

**Solutions:**

**1. Split large documents:**
```python
# Split into smaller files
with open("large_doc.txt", "r") as f:
    content = f.read()

# Split by sections, chapters, etc.
sections = content.split("\n\n## ")  # Markdown sections

for i, section in enumerate(sections):
    upload_request({
        "text": section,
        "title": f"Large Doc - Part {i+1}"
    })
```

**2. Disable AI tagging for large uploads:**
```python
# Fast mode - no AI tagging
data = {
    "text": content,
    "title": "My Doc",
    "use_ai_tagging": False  # This is default, but be explicit
}
```

**3. Increase timeout:**
```python
import requests

response = requests.post(
    "http://146.190.169.226:8000/upload",
    json=data,
    timeout=300  # 5 minutes instead of 120 seconds
)
```

**4. Use batch upload script:**
See `/backend/ingest_content_UPDATED.py` for production-ready batch uploads with:
- Automatic retry
- Progress tracking
- Error handling

---

### Upload Succeeds But Shows 0 Vectors Uploaded

**Response:**
```json
{
  "status": "success",
  "chunks_created": 47,
  "vectors_uploaded": 0
}
```

**Causes:**
1. Pinecone upsert failed silently
2. Encoding issues with metadata
3. API key issues

**Debug:**
```bash
# Check server logs
ssh root@146.190.169.226
journalctl -u main -f

# Look for:
# - "Error upserting batch"
# - Unicode/encoding errors
# - Pinecone API errors
```

**Solutions:**

**1. Check encoding:**
```python
# Text has problematic characters
text = "Smart quotes: \u201C\u201D"  # Bad

# Solution: Clean text first
import unicodedata

def clean_text(text):
    # Normalize to ASCII
    text = text.encode('ascii', errors='ignore').decode('ascii')
    return text

data = {
    "text": clean_text(original_text),
    "title": "My Doc"
}
```

**2. Verify Pinecone connection:**
```bash
curl http://146.190.169.226:8000/stats
```

Should show increased vector count after upload.

**3. Check Pinecone dashboard:**
- Go to https://app.pinecone.io
- Check `evolve-consciousness` index
- Verify vector count increased

---

### Upload Fails with "Embedding generation failed"

**Error:**
```json
{
  "detail": "Embedding generation failed: API key invalid"
}
```

**Causes:**
1. OpenAI API key is invalid or expired
2. OpenAI billing issue (no credits)
3. Rate limit exceeded

**Solutions:**

**1. Verify API key:**
```bash
ssh root@146.190.169.226
cat /opt/conscious-engine/backend/.env | grep OPENAI
```

**2. Test OpenAI directly:**
```bash
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer YOUR_API_KEY"
```

Should return list of models. If it fails, your API key is invalid.

**3. Check billing:**
- Go to https://platform.openai.com/account/billing
- Verify you have credits
- Check usage limits

**4. Restart server with new API key:**
```bash
ssh root@146.190.169.226
cd /opt/conscious-engine/backend
nano .env  # Update OPENAI_API_KEY
systemctl restart main
```

---

### Upload Fails with Null Metadata Error

**Error:**
```
TypeError: 'NoneType' object is not subscriptable
```

**Cause:** Tagging function returned None instead of dict

**Debug:**
```bash
# Check logs
ssh root@146.190.169.226
journalctl -u main -f
```

**Solution:**
Update `/backend/tagging.py` to always return a valid dict:

```python
def generate_tags(...):
    try:
        # ... tagging logic ...
        return tags_dict
    except Exception as e:
        # Fallback to empty but valid structure
        return {
            "tags": [],
            "detected_categories": {},
            "primary_theme": "",
            "consciousness_level": "neutrality",
            "emotions": [],
            # ... all other fields ...
        }
```

---

### Document Uploaded But Not Appearing in /uploaded-documents

**Symptom:**
Upload succeeds, but document doesn't show in document list.

**Causes:**
1. Database has >10,000 vectors (query limit)
2. Title was encoded incorrectly
3. Cache issue

**Solutions:**

**1. Check stats first:**
```bash
curl http://146.190.169.226:8000/stats
```

If `total_vectors` increased, upload worked.

**2. Search for it directly:**
```bash
curl -X POST http://146.190.169.226:8000/check-duplicate \
  -H "Content-Type: application/json" \
  -d '{"title": "Your Document Title"}'
```

**3. Query for it:**
```bash
curl -X POST http://146.190.169.226:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "content from your document",
    "filters": {"title": "Your Document Title"}
  }'
```

**4. If you have >10K vectors:**
The `/uploaded-documents` endpoint has a Pinecone limit. Use filters:

```python
# Get documents by prefix
response = requests.post("/query", json={
    "question": "any question",
    "filters": {"title": {"$regex": "^Beginner.*"}}
})
```

---

## Query Issues

### Query Returns "No Relevant Information Found"

**Response:**
```json
{
  "answer": "I couldn't find relevant information in the knowledge base to answer your question.",
  "sources": [],
  "metadata": {"matches_found": 0}
}
```

**Causes:**
1. Database is empty
2. Filters are too restrictive
3. Question doesn't match content
4. Embeddings aren't semantically similar

**Debug:**

**Step 1: Check database has content:**
```bash
curl http://146.190.169.226:8000/stats
```

If `total_vectors: 0`, you need to upload content first.

**Step 2: Try query without filters:**
```bash
curl -X POST http://146.190.169.226:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "consciousness",
    "filters": {},
    "top_k": 10
  }'
```

**Step 3: Check what's actually in the database:**
```bash
curl http://146.190.169.226:8000/uploaded-documents
```

**Solutions:**

**1. Remove overly restrictive filters:**
```python
# Too restrictive - may return 0 results
filters = {
    "tradition": "vedic",
    "teacher": "blavatsky",  # Blavatsky isn't Vedic!
    "primary_chakra": "heart"
}

# Better - start broad
filters = {
    "all_chakras": {"$in": ["heart"]}
}
```

**2. Rephrase question to match content:**
```python
# If your content uses "awareness" not "consciousness"
# Bad
question = "What is consciousness?"

# Better
question = "What is awareness?"
```

**3. Increase top_k:**
```python
# Default is 5, try more
data = {
    "question": "...",
    "top_k": 20
}
```

**4. Use semantic terms from your content:**
Look at your uploaded documents' tags and use those keywords in questions.

---

### Query Returns Irrelevant Results

**Symptom:**
Results don't match the question well.

**Causes:**
1. `top_k` is too high
2. Database content doesn't match domain
3. Question is too vague
4. Filters aren't helping

**Solutions:**

**1. Reduce top_k:**
```python
# Too many results = lower quality
data = {"question": "...", "top_k": 20}  # Bad

# Better - most relevant only
data = {"question": "...", "top_k": 3}
```

**2. Add filters:**
```python
# Vague question
data = {"question": "How do I heal?"}

# Better - targeted with filters
data = {
    "question": "How do I heal?",
    "filters": {
        "all_chakras": {"$in": ["heart"]},
        "healing_modality": "breathwork"
    }
}
```

**3. Make question more specific:**
```python
# Vague
"Tell me about consciousness"

# Specific
"How does the heart chakra relate to consciousness in Vedic tradition?"
```

**4. Check program_level matches content:**
```python
# If all your content is advanced, but you query at beginner level
data = {
    "question": "...",
    "program_level": "beginner"  # Mismatch!
}

# Better - match your content
data = {
    "question": "...",
    "program_level": "advanced"
}
```

---

### Query Succeeds But Answer is Truncated

**Symptom:**
Answer cuts off mid-sentence.

**Cause:** Claude's `max_tokens` limit reached (default: 2000)

**Solution:**
Modify `/backend/main.py`:

```python
# Line ~225
message = anthropic_client.messages.create(
    model=CLAUDE_MODEL,
    max_tokens=4000,  # Increase from 2000
    messages=[{"role": "user", "content": prompt}]
)
```

**Warning:** Higher tokens = higher cost per query.

---

### Query Works But Sources Are Empty

**Response:**
```json
{
  "answer": "...",
  "sources": [],
  "metadata": {"matches_found": 5}
}
```

**Cause:** Bug in source formatting (rare)

**Debug:**
Check `/backend/main.py` around line 509:

```python
sources = [
    {
        "title": match.metadata.get("title", "Unknown"),
        "source": match.metadata.get("source", "Unknown"),
        "score": match.score,
        "tags": match.metadata.get("tags", [])
    }
    for match in matches
]
```

Ensure metadata fields exist.

---

## Server Issues

### Server Not Starting

**Symptom:**
```bash
systemctl status main
# Shows: failed (Result: exit-code)
```

**Debug:**
```bash
# Check logs
journalctl -u main -n 50

# Common errors:
# - ModuleNotFoundError
# - API key errors
# - Port already in use
```

**Solutions:**

**1. ModuleNotFoundError:**
```bash
ssh root@146.190.169.226
cd /opt/conscious-engine/backend
source venv/bin/activate
pip install -r requirements.txt
systemctl restart main
```

**2. API Key Errors:**
```bash
# Check .env file
cat /opt/conscious-engine/backend/.env

# Verify all keys are set:
# - PINECONE_API_KEY
# - OPENAI_API_KEY
# - ANTHROPIC_API_KEY

# Update if needed
nano /opt/conscious-engine/backend/.env
systemctl restart main
```

**3. Port Already in Use:**
```bash
# Check what's using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or change port in main.py
nano /opt/conscious-engine/backend/main.py
# Change: uvicorn.run(app, host="0.0.0.0", port=8001)

systemctl restart main
```

**4. Pinecone Index Doesn't Exist:**
```bash
# Server tries to create index but fails
# Check logs for: "Failed to create index"

# Solution: Create manually
# Go to https://app.pinecone.io
# Create index:
#   Name: evolve-consciousness
#   Dimensions: 1536
#   Metric: cosine
#   Cloud: AWS
#   Region: us-east-1
```

---

### Server Running But Unresponsive

**Symptom:**
```bash
systemctl status main
# Shows: active (running)

curl http://146.190.169.226:8000/health
# Hangs or times out
```

**Causes:**
1. Server is processing a large upload
2. Memory exhausted
3. Pinecone connection hung
4. Thread deadlock

**Solutions:**

**1. Check server resources:**
```bash
ssh root@146.190.169.226

# Check memory
free -h

# Check CPU
top

# Check disk
df -h
```

**2. Restart server:**
```bash
systemctl restart main

# Wait 10 seconds
sleep 10

# Test
curl http://146.190.169.226:8000/health
```

**3. Check for hung processes:**
```bash
ps aux | grep python
# Look for high CPU/memory usage

# If needed, force kill
pkill -9 -f "main.py"
systemctl start main
```

**4. Increase server resources:**
- Upgrade DigitalOcean droplet to 4GB+ RAM
- Or optimize code to use less memory

---

### Server Crashes Repeatedly

**Symptom:**
```bash
systemctl status main
# Shows: active (running)

# But crashes after a few minutes
journalctl -u main -f
# Shows repeating crash/restart cycle
```

**Causes:**
1. Memory leak
2. Unhandled exception in request handler
3. API rate limits
4. Database connection issues

**Debug:**
```bash
# Check logs for patterns
journalctl -u main -n 200 | grep -i error

# Common errors:
# - "Out of memory"
# - "Rate limit exceeded"
# - "Connection reset"
# - Unhandled Python exceptions
```

**Solutions:**

**1. Memory Issues:**
```bash
# Check memory usage
free -h

# If memory is low, restart server
systemctl restart main

# Long-term: Upgrade droplet or optimize code
```

**2. Rate Limit Issues:**
```python
# Add rate limiting to upload endpoint
# In main.py, add delay between chunks

import time

for chunk in chunks:
    # ... process chunk ...
    time.sleep(0.1)  # 100ms delay between embeddings
```

**3. Unhandled Exceptions:**
Look for specific error in logs, then add error handling:

```python
# Example: Handle Pinecone timeouts
try:
    index.upsert(vectors=vectors_to_upsert)
except Exception as e:
    logger.error(f"Upsert failed: {e}")
    # Retry or skip
```

---

### Server Logs Show API Key Warnings

**Symptom:**
```bash
journalctl -u main -f
# Shows: "API key not found" or "Invalid API key"
```

**Solution:**
```bash
# Check environment variables
ssh root@146.190.169.226
cd /opt/conscious-engine/backend
cat .env

# Verify all keys are present and valid
# Format should be:
PINECONE_API_KEY=pcsk_...
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# If missing, add them
nano .env

# Restart server
systemctl restart main
```

---

## Connection Issues

### Cannot SSH to Server

**Symptom:**
```bash
ssh root@146.190.169.226
# Connection refused or timeout
```

**Causes:**
1. Server is down
2. Firewall blocking port 22
3. Wrong IP address
4. SSH keys changed

**Solutions:**

**1. Check server is running:**
- Go to DigitalOcean dashboard
- Check droplet status
- If powered off, power on

**2. Use DigitalOcean console:**
- DigitalOcean dashboard → Droplets → Your droplet
- Click "Console" or "Access"
- Log in directly through web interface

**3. Check firewall:**
```bash
# Once logged in via console
ufw status

# If SSH is blocked, allow it
ufw allow 22
```

**4. Reset SSH keys (if needed):**
- DigitalOcean dashboard → Droplets → Your droplet
- Settings → Access → Reset Root Password
- Use password to log in, then add your SSH key

---

### API Requests Time Out

**Symptom:**
```bash
curl http://146.190.169.226:8000/health
# Hangs for 30+ seconds, then fails
```

**Causes:**
1. Server is overloaded
2. Network issue
3. Firewall blocking port 8000
4. Server not listening on public IP

**Solutions:**

**1. Check server is listening:**
```bash
ssh root@146.190.169.226
netstat -tlnp | grep 8000

# Should show:
# tcp  0  0  0.0.0.0:8000  0.0.0.0:*  LISTEN  12345/python

# If not listening on 0.0.0.0, check main.py:
# uvicorn.run(app, host="0.0.0.0", port=8000)  # NOT "localhost"
```

**2. Check firewall:**
```bash
ufw status

# Allow port 8000
ufw allow 8000

# Or if using nginx, allow 80/443
ufw allow 80
ufw allow 443
```

**3. Test locally first:**
```bash
ssh root@146.190.169.226
curl http://localhost:8000/health

# If this works but external doesn't, it's a firewall/network issue
```

**4. Check DigitalOcean firewall:**
- Dashboard → Networking → Firewalls
- Ensure port 8000 is allowed
- Or use nginx on port 80 (always allowed)

---

### Cannot Connect to Pinecone

**Symptom:**
```bash
curl http://146.190.169.226:8000/health
# Returns:
{
  "status": "unhealthy",
  "error": "Failed to connect to Pinecone"
}
```

**Causes:**
1. Invalid Pinecone API key
2. Index doesn't exist
3. Network issue (unlikely - Pinecone is cloud)
4. Pinecone service outage

**Solutions:**

**1. Verify API key:**
```bash
ssh root@146.190.169.226
cat /opt/conscious-engine/backend/.env | grep PINECONE

# Test the key
# Go to https://app.pinecone.io
# API Keys → Verify your key
```

**2. Check index exists:**
```bash
# In Python shell
python3
>>> from pinecone import Pinecone
>>> pc = Pinecone(api_key="YOUR_KEY")
>>> pc.list_indexes()
# Should include 'evolve-consciousness'
```

**3. Create index if missing:**
```python
from pinecone import Pinecone, ServerlessSpec

pc = Pinecone(api_key="YOUR_KEY")
pc.create_index(
    name="evolve-consciousness",
    dimension=1536,
    metric="cosine",
    spec=ServerlessSpec(cloud="aws", region="us-east-1")
)
```

**4. Check Pinecone status:**
- Go to https://status.pinecone.io
- Verify no outages

---

## MCP Server Issues

### MCP Server Won't Connect

**Symptom:**
Claude Desktop or MCP client can't connect to server.

**Causes:**
1. SSH tunnel not established
2. Server not running
3. Wrong port configuration
4. MCP server config incorrect

**Solutions:**

**1. Start SSH tunnel:**
```bash
# On your local machine
ssh -L 8000:localhost:8000 root@146.190.169.226 -N

# Keep this running in background
# Or use screen/tmux
```

**2. Verify tunnel:**
```bash
# On local machine
curl http://localhost:8000/health

# Should return server health
```

**3. Check MCP config:**
If using MCP server, check config file (usually `mcp_config.json`):

```json
{
  "servers": {
    "evolve": {
      "url": "http://localhost:8000",
      "timeout": 30
    }
  }
}
```

**4. Test direct connection:**
```bash
# Skip MCP, test API directly
curl http://146.190.169.226:8000/health
```

---

### SSH Tunnel Keeps Dropping

**Symptom:**
SSH tunnel works initially but disconnects after inactivity.

**Solution:**

**Use autossh for persistent tunnels:**
```bash
# Install autossh
brew install autossh  # macOS
# or
sudo apt install autossh  # Linux

# Create persistent tunnel
autossh -M 0 -f -N -L 8000:localhost:8000 root@146.190.169.226 \
  -o "ServerAliveInterval 30" \
  -o "ServerAliveCountMax 3"
```

**Or use SSH config:**
```bash
# ~/.ssh/config
Host evolve
  HostName 146.190.169.226
  User root
  LocalForward 8000 localhost:8000
  ServerAliveInterval 30
  ServerAliveCountMax 3
  ControlMaster auto
  ControlPath ~/.ssh/control-%r@%h:%p
  ControlPersist 10m

# Then connect with:
ssh evolve -N

# Tunnel stays alive even if connection drops
```

---

## Performance Issues

### Queries Are Slow (>10 seconds)

**Causes:**
1. `top_k` is too high
2. Database is very large
3. Complex filters
4. Claude is slow

**Solutions:**

**1. Reduce top_k:**
```python
# Default is 5, which is usually fine
# If you increased it, reduce back
data = {"question": "...", "top_k": 5}
```

**2. Simplify filters:**
```python
# Complex filter
filters = {
    "all_chakras": {"$in": ["heart", "crown", "third_eye"]},
    "all_traditions": {"$in": ["vedic", "buddhist"]},
    "consciousness_level": {"$in": ["love", "joy"]}
}

# Simpler filter
filters = {
    "primary_chakra": "heart"
}
```

**3. Use caching:**
```python
# Cache common queries
import functools

@functools.lru_cache(maxsize=100)
def cached_query(question, filters_json):
    return requests.post("/query", json={
        "question": question,
        "filters": json.loads(filters_json)
    }).json()
```

**4. Profile the query:**
```python
import time

start = time.time()
result = query(...)
print(f"Query took {time.time() - start:.2f}s")

# Breakdown:
# - Embedding generation: ~0.5s
# - Pinecone search: ~0.5-2s
# - Claude answer: ~3-8s
```

---

### Uploads Are Slow

**Causes:**
1. AI tagging enabled
2. Large documents
3. Network speed
4. Server resources

**Solutions:**

**1. Disable AI tagging:**
```python
# Slow (with AI)
data = {"text": "...", "title": "...", "use_ai_tagging": True}

# Fast (keyword only)
data = {"text": "...", "title": "...", "use_ai_tagging": False}
```

**2. Use batch upload script:**
```bash
# Production batch upload with optimizations
cd /opt/conscious-engine/backend
python ingest_content_UPDATED.py /content --level beginner

# Features:
# - Rate limiting (0.5s between uploads)
# - Error handling
# - Progress tracking
```

**3. Split large documents:**
```python
# Don't upload 500KB files in one go
# Split by sections first
```

**4. Upload during off-hours:**
If server is shared, upload when usage is low.

---

### Server Memory Usage Keeps Growing

**Symptom:**
```bash
free -h
# Shows memory usage climbing over time
```

**Cause:** Memory leak (likely in Python code)

**Solutions:**

**1. Restart server periodically:**
```bash
# Add cron job to restart daily at 4am
crontab -e

# Add line:
0 4 * * * /bin/systemctl restart main
```

**2. Find the leak:**
```python
# Add memory profiling
import tracemalloc

tracemalloc.start()

# ... your code ...

snapshot = tracemalloc.take_snapshot()
top_stats = snapshot.statistics('lineno')

for stat in top_stats[:10]:
    print(stat)
```

**3. Optimize code:**
Common memory issues:
- Large lists not being cleared
- Caching too much data
- Not closing connections

---

## Data Issues

### Duplicate Documents in Database

**Symptom:**
Same document appears multiple times in `/uploaded-documents`.

**Cause:** Document was uploaded multiple times with same title.

**Solution:**

**1. Check duplicates:**
```bash
curl http://146.190.169.226:8000/uploaded-documents | jq '.documents | group_by(.title) | map(select(length > 1))'
```

**2. Delete duplicates:**
```bash
# Delete by title (deletes ALL chunks with that title)
curl -X DELETE http://146.190.169.226:8000/delete-document/Duplicate%20Title
```

**3. Prevent future duplicates:**
```python
import requests

def upload_if_not_exists(text, title):
    # Check if exists
    check = requests.post("/check-duplicate", json={"title": title}).json()

    if check["exists"]:
        print(f"'{title}' already exists, skipping")
        return False

    # Upload
    requests.post("/upload", json={"text": text, "title": title})
    return True
```

---

### Missing Metadata Fields

**Symptom:**
Some chunks are missing expected metadata (e.g., no `primary_chakra`).

**Causes:**
1. Content doesn't match keywords
2. Tagging function failed
3. Field was added after upload

**Solutions:**

**1. Check what was detected:**
```python
# Query and inspect metadata
result = requests.post("/query", json={
    "question": "anything",
    "filters": {"title": "Your Document"},
    "top_k": 1
}).json()

print(result["sources"][0])  # Check metadata fields
```

**2. Re-upload with AI tagging:**
```python
# Delete old version
requests.delete("/delete-document/Your%20Document")

# Upload with AI tagging for better detection
requests.post("/upload", json={
    "text": content,
    "title": "Your Document",
    "use_ai_tagging": True,
    "ai_provider": "ollama"
})
```

**3. Update tagging keywords:**
If keyword-based tagging is missing concepts, update `/backend/tagging.py` keyword dictionaries.

---

### Incorrect Metadata Values

**Symptom:**
Metadata field has wrong value (e.g., `primary_chakra: "crown"` when content is about root chakra).

**Causes:**
1. Keyword ambiguity
2. AI tagging hallucination
3. Multiple concepts in same chunk

**Solutions:**

**1. Use more specific content:**
Split chunks that discuss multiple topics.

**2. Manual override:**
Currently not supported - would need to add custom metadata parameter to upload endpoint.

**Future feature:**
```python
# Override auto-detected tags
requests.post("/upload", json={
    "text": content,
    "title": "My Doc",
    "metadata_override": {
        "primary_chakra": "root",
        "tradition": "vedic"
    }
})
```

---

## Cost & Spending Issues

### Spending Dashboard Shows $0 Despite Usage

**Symptom:**
```bash
curl http://146.190.169.226:8000/spending-dashboard
# Returns: "total_cost": 0.00
```

**Cause:** Spending tracker only tracks Claude analyses, NOT queries or uploads.

**Explanation:**
- `/upload` uses OpenAI (not tracked)
- `/query` uses Claude but doesn't record to spending DB
- Only custom analysis jobs record spending

**To track query costs:**
You'd need to modify `/backend/main.py` to record every query. Currently not implemented.

---

### Budget Exceeded Warning

**Response:**
```json
{
  "budget": {
    "can_proceed": false,
    "would_exceed_by": 5.23
  }
}
```

**Solution:**

**1. Increase monthly cap:**
```bash
curl -X POST http://146.190.169.226:8000/update-spending-cap \
  -H "Content-Type: application/json" \
  -d '{"new_cap": 40.00}'
```

**2. Wait for next month:**
Cap resets on the 1st of each month.

**3. Optimize analysis:**
```python
# Reduce scope
estimate = requests.post("/estimate-analysis-cost", json={
    "analysis_type": "recent",
    "limit": 25  # Reduce from 50
}).json()
```

---

### Unexpected High Costs

**Symptom:**
Monthly bill is higher than expected.

**Debug:**

**1. Check spending history:**
```bash
curl http://146.190.169.226:8000/spending-dashboard | jq '.history'
```

**2. Review what analyses ran:**
```json
{
  "history": [
    {
      "timestamp": "2025-11-30 14:23:45",
      "analysis_type": "full",  // ← Full database = expensive
      "document_count": 2000,
      "total_cost": 23.45
    }
  ]
}
```

**3. Check OpenAI usage:**
- Go to https://platform.openai.com/usage
- Check embeddings usage (for uploads)

**4. Check Anthropic usage:**
- Go to https://console.anthropic.com/settings/billing
- Check Claude API usage (for queries)

**Solutions:**
- Use AI tagging sparingly
- Reduce `top_k` in queries (fewer results = less context = lower cost)
- Cache common query results
- Use keyword tagging instead of AI tagging

---

## Debug Procedures

### Full System Health Check

```bash
#!/bin/bash
# Run this script to check everything

echo "=== SERVER STATUS ==="
systemctl status main | head -n 3

echo -e "\n=== API HEALTH ==="
curl -s http://146.190.169.226:8000/health | jq .

echo -e "\n=== DATABASE STATS ==="
curl -s http://146.190.169.226:8000/stats | jq .

echo -e "\n=== RECENT LOGS ==="
journalctl -u main -n 20 --no-pager

echo -e "\n=== MEMORY USAGE ==="
free -h

echo -e "\n=== DISK USAGE ==="
df -h | grep -v loop

echo -e "\n=== PROCESS STATUS ==="
ps aux | grep python | grep -v grep
```

Save as `check_health.sh`, then:
```bash
chmod +x check_health.sh
./check_health.sh
```

---

### Test Upload Pipeline

```bash
#!/bin/bash
# Test the complete upload flow

echo "Testing upload pipeline..."

# Test 1: Upload
echo -e "\n[1/4] Testing upload..."
UPLOAD_RESPONSE=$(curl -s -X POST http://146.190.169.226:8000/upload \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Test document about heart chakra healing and forgiveness.",
    "title": "Test Document"
  }')

echo "$UPLOAD_RESPONSE" | jq .

# Test 2: Check it exists
echo -e "\n[2/4] Checking duplicate..."
CHECK_RESPONSE=$(curl -s -X POST http://146.190.169.226:8000/check-duplicate \
  -H "Content-Type: application/json" \
  -d '{"title": "Test Document"}')

echo "$CHECK_RESPONSE" | jq .

# Test 3: Query for it
echo -e "\n[3/4] Querying..."
QUERY_RESPONSE=$(curl -s -X POST http://146.190.169.226:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Tell me about heart chakra healing",
    "filters": {"title": "Test Document"}
  }')

echo "$QUERY_RESPONSE" | jq '.metadata'

# Test 4: Delete it
echo -e "\n[4/4] Cleaning up..."
DELETE_RESPONSE=$(curl -s -X DELETE http://146.190.169.226:8000/delete-document/Test%20Document)

echo "$DELETE_RESPONSE" | jq .

echo -e "\n✓ Pipeline test complete"
```

---

### Debug Specific Upload

```python
import requests
import json

def debug_upload(file_path):
    """Debug why a specific file won't upload"""

    # Read file
    with open(file_path, 'r') as f:
        content = f.read()

    print(f"File: {file_path}")
    print(f"Size: {len(content)} characters")
    print(f"Encoding issues: {len([c for c in content if ord(c) > 127])} non-ASCII chars")

    # Clean content
    clean_content = content.encode('ascii', errors='ignore').decode('ascii')

    # Try upload with detailed error handling
    try:
        response = requests.post(
            "http://146.190.169.226:8000/upload",
            json={
                "text": clean_content,
                "title": file_path.split('/')[-1]
            },
            timeout=120
        )

        if response.status_code == 200:
            print("✓ Upload successful")
            print(response.json())
        else:
            print(f"✗ Upload failed: {response.status_code}")
            print(response.text)

    except requests.exceptions.Timeout:
        print("✗ Upload timed out (>120s)")
        print(f"Try splitting into smaller files")

    except Exception as e:
        print(f"✗ Error: {e}")

# Usage
debug_upload("/path/to/problematic/file.md")
```

---

## Log Files

### Server Logs

**Location:** Systemd journal (not a file)

**View logs:**
```bash
# Last 50 lines
journalctl -u main -n 50

# Follow in real-time
journalctl -u main -f

# Filter by time
journalctl -u main --since "2025-11-30 10:00:00"
journalctl -u main --since "1 hour ago"

# Search for errors
journalctl -u main | grep -i error

# Export to file
journalctl -u main --since today > /tmp/logs.txt
```

### Application Logs

**Location:** Set by logging configuration in `main.py`

**Current:** Logs to stdout (captured by systemd)

**To add file logging:**
```python
# In main.py
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("/var/log/evolve/app.log"),
        logging.StreamHandler()
    ]
)
```

### Pinecone Logs

**Not available** - Pinecone is a cloud service

**To debug Pinecone issues:**
- Check Pinecone dashboard: https://app.pinecone.io
- Check status page: https://status.pinecone.io
- Review vector counts and index stats

### OpenAI Logs

**Not available** - Use OpenAI dashboard

**To track usage:**
- Go to https://platform.openai.com/usage
- Filter by date range
- Download CSV for detailed analysis

### Anthropic Logs

**Not available** - Use Anthropic dashboard

**To track usage:**
- Go to https://console.anthropic.com/settings/billing
- View usage by day
- Check rate limits

---

## When to Restart

### Restart the Server

**When:**
- After config changes (`.env` file)
- After code changes
- Memory usage is high
- Server is unresponsive
- After package updates

**How:**
```bash
ssh root@146.190.169.226
systemctl restart main

# Wait for startup
sleep 5

# Verify
curl http://localhost:8000/health
```

### Restart the Droplet

**When:**
- System packages updated (kernel, etc.)
- Multiple services are failing
- Disk is full
- Network issues

**How:**
```bash
# Via SSH
ssh root@146.190.169.226
reboot

# Or via DigitalOcean dashboard
# Droplets → Your droplet → Power → Reboot
```

**Warning:** Server will be down for ~30 seconds.

### Restart Just Python Process

**When:**
- Testing code changes quickly
- Memory leak suspected
- Process hung but server is running

**How:**
```bash
ssh root@146.190.169.226

# Find process
ps aux | grep main.py

# Kill it
pkill -f main.py

# Systemd will auto-restart (if configured with Restart=always)
# Or start manually
systemctl start main
```

### Never Restart

**Don't restart for:**
- Slow individual queries (normal)
- Upload taking a long time (normal for large docs)
- Single failed request (investigate first)

---

## Emergency Procedures

### Complete System Recovery

If everything is broken:

```bash
# 1. SSH into server
ssh root@146.190.169.226

# 2. Stop server
systemctl stop main

# 3. Backup database (if using SQLite for spending)
cp backend/claude_spending.db backend/claude_spending.db.backup

# 4. Update code
cd /opt/conscious-engine
git pull

# 5. Reinstall dependencies
cd backend
source venv/bin/activate
pip install --upgrade -r requirements.txt

# 6. Test environment
python3 << EOF
import os
from dotenv import load_dotenv
load_dotenv()
print("Pinecone:", os.getenv("PINECONE_API_KEY")[:10])
print("OpenAI:", os.getenv("OPENAI_API_KEY")[:10])
print("Anthropic:", os.getenv("ANTHROPIC_API_KEY")[:10])
EOF

# 7. Start server
systemctl start main

# 8. Wait for startup
sleep 10

# 9. Test
curl http://localhost:8000/health

# 10. If still broken, check logs
journalctl -u main -n 100
```

### Database Corruption

If Pinecone data is corrupted:

**Warning:** This will delete ALL data!

```python
from pinecone import Pinecone

pc = Pinecone(api_key="YOUR_KEY")

# Delete index
pc.delete_index("evolve-consciousness")

# Recreate
from pinecone import ServerlessSpec

pc.create_index(
    name="evolve-consciousness",
    dimension=1536,
    metric="cosine",
    spec=ServerlessSpec(cloud="aws", region="us-east-1")
)

# Re-upload all content
# (Use ingest_content.py script)
```

---

## Support Resources

**Documentation:**
- [API Reference](API_REFERENCE.md)
- [Metadata Schema](METADATA_SCHEMA.md)
- [Deployment Guide](DEPLOYMENT_GUIDE.md)

**External Services:**
- Pinecone Dashboard: https://app.pinecone.io
- OpenAI Platform: https://platform.openai.com
- Anthropic Console: https://console.anthropic.com
- DigitalOcean: https://cloud.digitalocean.com

**Quick Help:**
```bash
# Test everything is working
curl http://146.190.169.226:8000/health | jq .

# Check database
curl http://146.190.169.226:8000/stats | jq .

# View recent logs
ssh root@146.190.169.226 'journalctl -u main -n 50'
```

---

**Last Updated:** November 30, 2025
**Version:** 1.0.0
