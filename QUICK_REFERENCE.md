# Evolve Consciousness Engine - Quick Reference

**Fast answers to common tasks**

---

## 🚀 Starting the Server

```bash
cd /opt/conscious-engine/backend
source venv/bin/activate
python main.py
```

Or if using systemd:
```bash
sudo systemctl start evolve
sudo systemctl status evolve
```

---

## 📤 Uploading Content

### **Single Directory**
```bash
python ingest_content.py /path/to/content --level beginner
```

### **With AI Tagging (slower, more accurate)**
```bash
python ingest_content.py /path/to/content --level beginner --ai-tagging
```

### **Specific File Pattern**
```bash
python ingest_content.py /path/to/content --level intermediate --pattern "*.txt"
```

### **Different API URL**
```bash
python ingest_content.py /path/to/content --api-url http://your-domain.com
```

---

## 🔍 Querying the System

### **Simple Query**
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the First Step?", "program_level": "beginner"}'
```

### **With Filters**
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Explain heart chakra activation",
    "program_level": "intermediate",
    "filters": {"chakra": "heart"},
    "top_k": 10
  }'
```

### **Advanced Level Query**
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How does Kabbalah relate to the 12 Steps?",
    "program_level": "advanced",
    "top_k": 5
  }'
```

---

## 📊 Checking Status

### **Health Check**
```bash
curl http://localhost:8000/health | python3 -m json.tool
```

### **Database Stats**
```bash
curl http://localhost:8000/stats | python3 -m json.tool
```

### **Service Logs**
```bash
sudo journalctl -u evolve -f
```

---

## 🛠️ Troubleshooting

### **Restart the Service**
```bash
sudo systemctl restart evolve
```

### **Check if Port is in Use**
```bash
sudo lsof -i :8000
```

### **Kill Process on Port 8000**
```bash
sudo kill $(sudo lsof -t -i:8000)
```

### **View Environment Variables**
```bash
cat /opt/conscious-engine/backend/.env
```

### **Test Pinecone Connection**
```python
from pinecone import Pinecone
import os
from dotenv import load_dotenv

load_dotenv()
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index("evolve-consciousness")
print(index.describe_index_stats())
```

### **Test OpenAI Connection**
```python
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
response = client.embeddings.create(
    model="text-embedding-ada-002",
    input="test"
)
print("OpenAI connected:", len(response.data[0].embedding))
```

### **Test Anthropic Connection**
```python
from anthropic import Anthropic
import os
from dotenv import load_dotenv

load_dotenv()
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
message = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=100,
    messages=[{"role": "user", "content": "Hello"}]
)
print("Claude says:", message.content[0].text)
```

---

## 📝 Common Upload Patterns

### **Upload Notion Export**
```bash
# Beginner content
python ingest_content.py /path/to/notion/beginner --level beginner

# Intermediate content
python ingest_content.py /path/to/notion/intermediate --level intermediate

# Advanced content
python ingest_content.py /path/to/notion/advanced --level advanced
```

### **Upload Mixed Content**
```bash
# Process all markdown files in a directory tree
find /path/to/content -name "*.md" -type f | while read file; do
    python ingest_content.py "$(dirname "$file")" --level beginner
done
```

---

## 🔄 Updating the System

### **Pull Latest Code**
```bash
cd /opt/conscious-engine
git pull origin main
```

### **Update Dependencies**
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt --upgrade
```

### **Restart Service**
```bash
sudo systemctl restart evolve
```

---

## 🧪 Testing

### **Run Test Suite**
```bash
cd /opt/conscious-engine/backend
source venv/bin/activate
python test_api.py
```

### **Test Single Upload**
```bash
curl -X POST http://localhost:8000/upload \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Test content about consciousness",
    "title": "Test Document",
    "source": "test",
    "program_level": "beginner",
    "use_ai_tagging": false
  }'
```

---

## 🔐 Security

### **Regenerate API Keys**
1. Get new keys from providers
2. Update `.env` file
3. Restart service

### **Backup Database**
```bash
# Pinecone is cloud-hosted and automatically backed up
# To export vectors, use Pinecone console or API
```

### **View Service Status**
```bash
sudo systemctl status evolve
```

---

## 📈 Monitoring

### **Check Resource Usage**
```bash
htop
```

### **Monitor API Calls**
```bash
tail -f /var/log/evolve/api.log
```

### **Check Disk Space**
```bash
df -h
```

---

## 🎯 Quick Filters

Use these in your queries for targeted results:

```json
{
  "filters": {
    "chakra": "heart",
    "step": "step_1",
    "tradition": "hermetic",
    "consciousness_level": "acceptance",
    "teacher": "hawkins"
  }
}
```

---

## 💡 Pro Tips

1. **Use keyword tagging** for bulk uploads (faster, cheaper)
2. **Enable AI tagging** for critical content (more accurate)
3. **Query with filters** to narrow results
4. **Adjust top_k** based on context needs (3-10 is optimal)
5. **Monitor costs** via OpenAI and Anthropic dashboards
6. **Cache common queries** in your frontend
7. **Use program levels** to match user sophistication

---

## 📞 Emergency Commands

### **Stop Everything**
```bash
sudo systemctl stop evolve
sudo systemctl stop nginx
```

### **Start Everything**
```bash
sudo systemctl start evolve
sudo systemctl start nginx
```

### **Full Reset**
```bash
# WARNING: This deletes all vectors!
# Only use if you need to start fresh
python -c "from pinecone import Pinecone; import os; from dotenv import load_dotenv; load_dotenv(); pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY')); pc.delete_index('evolve-consciousness')"
```

---

**Keep this file handy for quick reference during development and deployment!**
