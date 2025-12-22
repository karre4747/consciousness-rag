# Evolve Consciousness Engine - Deployment & Usage Guide

**Version:** 1.1.0  
**Date:** December 21, 2025  
**Status:** Phase 1 Complete - Ready for Deployment

---

## 🎯 What You've Built

The **Evolve Consciousness Engine** is now a fully functional RAG (Retrieval-Augmented Generation) system that combines:

- ✅ **Pinecone Vector Database** - Cloud-hosted, scalable vector storage
- ✅ **OpenAI Embeddings** - Industry-standard semantic search (`text-embedding-ada-002`)
- ✅ **Claude Sonnet 4.5** - Latest AI model for intelligent, philosophical responses
- ✅ **Advanced Tagging System** - Automatic categorization of consciousness, recovery, and esoteric content
- ✅ **FastAPI Backend** - Production-ready REST API
- ✅ **Content Ingestion Pipeline** - Batch upload your entire content library

---

## 📋 Quick Answers to Your Questions

### **1. Do you need access to DigitalOcean?**

**No, I don't need access.** The system is designed to run independently on your DigitalOcean droplet. You'll deploy it yourself using the instructions below. Everything is containerized and ready to go.

### **2. Do you need to open ports?**

**Yes, but only standard web ports:**
- **Port 8000** - For the API (or 80/443 if you add nginx)
- **No inbound access needed for Pinecone** - It's cloud-hosted, your server connects outbound

### **3. How to start uploading content?**

**Three simple steps:**
1. Deploy the backend to DigitalOcean (see below)
2. Organize your content files (`.md`, `.txt`, etc.)
3. Run the ingestion script: `python ingest_content.py /path/to/your/content --level beginner`

---

## 🚀 Deployment to DigitalOcean

### **Prerequisites**

- DigitalOcean Droplet (Ubuntu 22.04, minimum 2GB RAM)
- SSH access to your droplet
- Domain name (optional, but recommended)

### **Step 1: Prepare Your Droplet**

SSH into your droplet:

```bash
ssh root@your-droplet-ip
```

Update system and install dependencies:

```bash
apt update && apt upgrade -y
apt install -y python3.11 python3.11-venv python3-pip git nginx
```

### **Step 2: Clone and Setup**

Clone your repository:

```bash
cd /opt
git clone https://github.com/karre4747/conscious-engine.git
cd conscious-engine/backend
```

Create virtual environment:

```bash
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### **Step 3: Configure Environment**

Create your `.env` file:

```bash
nano .env
```

Add your API keys (use the values from your local `.env`):

```env
# API Keys
PINECONE_API_KEY=your_pinecone_key_here
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here

# Pinecone Configuration
PINECONE_INDEX_NAME=evolve-consciousness
PINECONE_DIMENSION=1536

# Model Configuration
EMBEDDING_MODEL=text-embedding-ada-002
CLAUDE_MODEL=claude-sonnet-4-5-20250929

# Application Configuration
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```

Save and exit (`Ctrl+X`, then `Y`, then `Enter`).

### **Step 4: Create Service User & Systemd Service**

First, create a dedicated user for security (never run as root):

```bash
useradd -m -s /bin/bash evolve-engine
chown -R evolve-engine:evolve-engine /opt/conscious-engine
```

Now create the service file:

Create a service file to run the API automatically:

```bash
nano /etc/systemd/system/evolve.service
```

Add this content:

```ini
[Unit]
Description=Evolve Consciousness Engine API
After=network.target

[Service]
Type=simple
User=evolve-engine
WorkingDirectory=/opt/conscious-engine/backend
Environment="PATH=/opt/conscious-engine/backend/venv/bin"
ExecStart=/opt/conscious-engine/backend/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
systemctl daemon-reload
systemctl enable evolve
systemctl start evolve
systemctl status evolve
```

### **Step 5: Configure Nginx & Enforce HTTPS (Required)**

1. **Install Certbot**:
   ```bash
   apt install -y certbot python3-certbot-nginx
   ```

2. **Open Firewall Ports**:
   ```bash
   ufw allow 80
   ufw allow 443
   ufw enable
   ```

3. **Create Nginx Config**:
   ```bash
   nano /etc/nginx/sites-available/evolve
   ```

   Add basic HTTP config (Certbot will upgrade this):
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;  # Replace with your actual domain

       location / {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

4. **Enable Site & Obtain Certificate**:
   ```bash
   ln -s /etc/nginx/sites-available/evolve /etc/nginx/sites-enabled/
   nginx -t && systemctl restart nginx
   
   # Run Certbot to obtain SSL and auto-configure Nginx
   certbot --nginx -d your-domain.com
   ```
   *Select Option 2 (Redirect) when asked to ensure all traffic is securely encrypted.*

5. **Verify Auto-Renewal**:
   ```bash
   systemctl status certbot.timer
   ```

### **Step 6: Verify Deployment**

Test the API:

```bash
curl http://localhost:8000/health
```

You should see:

```json
{
  "status": "healthy",
  "pinecone": {
    "connected": true,
    "index": "evolve-consciousness",
    "total_vectors": 0
  },
  "openai": {"connected": true},
  "anthropic": {"connected": true}
}
```

---

## 📚 Content Ingestion Guide

### **Organizing Your Content**

Create a directory structure like this:

```
/opt/content/
├── beginner/
│   ├── 12_steps_intro.md
│   ├── consciousness_basics.md
│   └── recovery_foundations.md
├── intermediate/
│   ├── quantum_consciousness.md
│   ├── mystical_traditions.md
│   └── neuroscience_recovery.md
└── advanced/
    ├── hermetic_principles.md
    ├── esoteric_teachings.md
    └── consciousness_mastery.md
```

### **Upload Content**

**For Beginner Level:**

```bash
cd /opt/conscious-engine/backend
source venv/bin/activate
python ingest_content.py /opt/content/beginner --level beginner
```

**For Intermediate Level:**

```bash
python ingest_content.py /opt/content/intermediate --level intermediate
```

**For Advanced Level:**

```bash
python ingest_content.py /opt/content/advanced --level advanced
```

**With AI-Enhanced Tagging (slower but more accurate):**

```bash
python ingest_content.py /opt/content/beginner --level beginner --ai-tagging
```

### **Upload Your Notion Documents**

You already have consolidated documents in `/home/ubuntu/notion_consolidation/`. However, since the service runs as `root` (or a specific service user), we need to ensure it can read these files.

**Recommendation:** Move the files to a shared location like `/opt/content/` and set permissions.

```bash
# 1. Create a shared content directory
mkdir -p /opt/content/notion_consolidation

# 2. Copy your files (preserving directory structure)
cp -r /home/ubuntu/notion_consolidation/* /opt/content/notion_consolidation/

# 3. Set ownership and permissions (service runs as evolve-engine)
chown -R evolve-engine:evolve-engine /opt/content
chmod -R 755 /opt/content

# 4. Verify permissions
ls -l /opt/content/notion_consolidation
```

**Now run the ingestion script pointing to the shared path (as the service user):**

```bash
sudo -u evolve-engine bash
source /opt/conscious-engine/backend/venv/bin/activate

# Upload the consolidated training documents
python ingest_content.py /opt/content/notion_consolidation --level beginner

# Upload the three-level program documents
python ingest_content.py /opt/content/notion_consolidation/BEGINNER* --level beginner
python ingest_content.py /opt/content/notion_consolidation/INTERMEDIATE* --level intermediate
python ingest_content.py /opt/content/notion_consolidation/ADVANCED* --level advanced
```

---

## 🧪 Testing the System

### **Test Upload Endpoint**

```bash
curl -X POST http://localhost:8000/upload \
  -H "Content-Type: application/json" \
  -d '{
    "text": "The First Step is about admitting powerlessness. This surrender opens the heart chakra and aligns with quantum consciousness principles.",
    "title": "Step 1 and Consciousness",
    "source": "test",
    "program_level": "beginner",
    "use_ai_tagging": false
  }'
```

### **Test Query Endpoint**

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How does the First Step relate to consciousness?",
    "program_level": "beginner",
    "top_k": 3
  }'
```

### **Check Database Stats**

```bash
curl http://localhost:8000/stats
```

---

## 🔧 API Endpoints & Security Reference

### 🛡️ Authentication & Security (CRITICAL)

**Production deployments MUST implement:**
1.  **API Key Authentication**: Require `X-API-Key` header for ALL endpoints.
2.  **Role-Based Access Control (RBAC)**:
    -   `ReadOnly` keys for `/query`
    -   `Admin` keys for `/upload` and `/delete`
3.  **Rate Limiting**:
    -   **Global**: 60 requests/minute/IP
    -   **Uploads**: 10 requests/minute (prevent vector spam)
    -   **Response**: Return `429 Too Many Requests` with `Retry-After` header.

### **Security Migration Checklist**
- [ ] Generate secure API keys (e.g., `openssl rand -hex 32`)
- [ ] Configure RBAC middleware (verify keys against stored hash)
- [ ] Enable Nginx Rate Limiting (`limit_req_zone`)
- [ ] Rotate keys quarterly

---

### **GET /**

### **GET /**
Health check - returns service status

### **GET /health**
Detailed health check with Pinecone stats

### **GET /stats**
Database statistics (total vectors, namespaces)

### **POST /upload**
**Security**: `Admin` Key Required. Rate limit: 10/min.

Upload and process a document

**Request Body:**
```json
{
  "text": "Document content here...",
  "title": "Document Title",
  "source": "Source identifier",
  "program_level": "beginner|intermediate|advanced",
  "use_ai_tagging": false
}
```

**Required Headers:**
- `X-API-Key`: `<Your-Admin-Key>`


**Response:**
```json
{
  "status": "success",
  "message": "Document 'Title' processed successfully",
  "chunks_created": 5,
  "vectors_uploaded": 5
}
```

### **POST /query**
Query the knowledge base

**Request Body:**
```json
{
  "question": "Your question here",
  "program_level": "beginner",
  "filters": {},
  "top_k": 5
}
```

**Response:**
```json
{
  "answer": "Comprehensive answer from Claude...",
  "sources": [
    {
      "title": "Source Document",
      "source": "path/to/doc",
      "score": 0.95,
      "tags": ["step_1", "heart", "consciousness"]
    }
  ],
  "metadata": {
    "matches_found": 5,
    "program_level": "beginner",
    "model": "claude-sonnet-4-5-20250929"
  }
}
```

---

## 🎨 Next Steps: Building the Frontend

Once your backend is deployed and content is uploaded, you can:

1. **Build a simple web interface** using React, Vue, or plain HTML/JavaScript
2. **Create a chat interface** that calls the `/query` endpoint
3. **Add user authentication** to track user progress
4. **Implement program level switching** (beginner → intermediate → advanced)
5. **Add fine-tuned models** for each persona (Phase 3 of your plan)

---

## 🐛 Troubleshooting

### **Service won't start**

Check logs:
```bash
journalctl -u evolve -f
```

### **Can't connect to Pinecone**

Verify API key:
```bash
cat /opt/conscious-engine/backend/.env | grep PINECONE
```

### **OpenAI errors**

Check your API key and billing status at https://platform.openai.com/

### **Slow responses**

- Reduce `top_k` in queries (default: 5)
- Disable AI tagging during ingestion
- Consider upgrading your droplet

---

## 📊 Cost Estimates

**Monthly Operating Costs:**

- **DigitalOcean Droplet** (2GB): ~$12/month
- **Pinecone** (Starter): Free for 100K vectors, then ~$70/month
- **OpenAI Embeddings**: ~$0.10 per 1M tokens (~$1-5/month for typical usage)
- **Claude API**: ~$3 per 1M input tokens (~$10-30/month depending on query volume)

**Total: ~$25-120/month** depending on usage

---

## 🎯 Success Metrics

Your system is working correctly when:

- ✅ `/health` endpoint returns "healthy"
- ✅ Content uploads successfully (check `/stats` for vector count)
- ✅ Queries return relevant, well-formatted answers
- ✅ Tags are being generated correctly
- ✅ Different program levels return appropriately-toned responses

---

## 📞 Support

If you encounter issues:

1. Check the logs: `journalctl -u evolve -f`
2. Verify all API keys are correct
3. Test each service individually (Pinecone, OpenAI, Anthropic)
4. Review the handoff document for architecture details

---

## 🎉 Congratulations!

You now have a production-ready consciousness and recovery RAG system. This is the foundation for all your future work:

- **Phase 2**: Content ingestion (you're ready!)
- **Phase 3**: Fine-tuning custom models for each persona
- **Phase 4**: Building the user interface and deployment

**The hard part is done. Now it's time to fill it with your wisdom and share it with the world.**

---

*Built with ❤️ for the evolution of human consciousness*
