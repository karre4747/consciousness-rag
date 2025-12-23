# Testing and Deployment Plan - Evolve Consciousness Engine

## 🎯 Overview

This guide walks you through testing and deploying the complete version of your Evolve Consciousness Engine on your Mac M1 Max.

---

## 📋 Pre-Deployment Checklist

Before you start, make sure you have:

- [ ] Mac M1 Max with 64GB RAM (you have this ✅)
- [ ] Python 3.11+ installed
- [ ] Git installed
- [ ] Pinecone account and API key
- [ ] OpenAI account and API key
- [ ] Anthropic (Claude) account and API key
- [ ] Terminal access

---

## 🚀 Step 1: Clone the Repository

### Option A: Fresh Clone (Recommended)

```bash
# Navigate to where you want the project
cd ~/Desktop  # or wherever you prefer

# Clone the repository
git clone https://github.com/karre4747/consciousness-rag.git

# Enter the directory
cd consciousness-rag

# Switch to the new branch
git checkout simplified-clean-2024

# Verify you're on the right branch
git branch --show-current
# Should show: simplified-clean-2024
```

### Option B: Update Existing Repository

```bash
# Navigate to your existing repository
cd /path/to/consciousness-rag

# Fetch latest changes
git fetch origin

# Switch to the new branch
git checkout simplified-clean-2024

# Pull latest changes
git pull origin simplified-clean-2024

# Verify you're on the right branch
git branch --show-current
# Should show: simplified-clean-2024
```

---

## 🔧 Step 2: Set Up Python Environment

### Create Virtual Environment

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Verify activation (should show venv in prompt)
which python
# Should show: /path/to/consciousness-rag/backend/venv/bin/python
```

### Install Dependencies

```bash
# Make sure you're in backend directory with venv activated
pip install --upgrade pip

# Install all dependencies
pip install -r requirements.txt

# Verify installation
pip list | grep -E "(pinecone|openai|anthropic|fastapi)"
```

**Expected output:**
```
anthropic          0.x.x
fastapi            0.x.x
openai             1.x.x
pinecone-client    3.x.x
```

---

## 🔑 Step 3: Configure API Keys

### Create .env File

```bash
# Make sure you're in backend directory
cd backend

# Create .env file
cat > .env << 'EOF'
# Pinecone Configuration
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_INDEX_NAME=consciousness-rag

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Anthropic (Claude) Configuration
ANTHROPIC_API_KEY=your_anthropic_api_key_here
CLAUDE_MODEL=claude-sonnet-4-20250514
EOF
```

### Add Your Actual API Keys

Edit the `.env` file and replace the placeholder values:

```bash
# Open in your preferred editor
nano .env
# or
vim .env
# or
code .env  # if using VS Code
```

**Replace:**
- `your_pinecone_api_key_here` → Your actual Pinecone API key
- `your_openai_api_key_here` → Your actual OpenAI API key
- `your_anthropic_api_key_here` → Your actual Anthropic API key

**Save and close the file.**

### Verify .env File

```bash
# Check that .env exists and has content
cat .env

# Make sure it's not tracked by git
git status .env
# Should show: nothing to commit (because .env is in .gitignore)
```

---

## 🧪 Step 4: Test the System

### Test 1: Start the Server

```bash
# Make sure you're in backend directory with venv activated
cd backend
source venv/bin/activate

# Start the server
python main_complete.py
```

**Expected output:**
```
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
Connected to Pinecone index: consciousness-rag
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

**If you see errors:**
- Check that all API keys are correct in `.env`
- Check that all dependencies are installed
- Check the error message for specific issues

### Test 2: Health Check

**Open a new terminal window** (keep the server running in the first one):

```bash
# Test the health endpoint
curl http://localhost:8000/health
```

**Expected output:**
```json
{
  "pinecone": "connected",
  "openai": "configured",
  "anthropic": "configured",
  "database": "initialized",
  "chunk_size": 1800
}
```

### Test 3: Open the Frontend

**Open your web browser** and navigate to:
```
http://localhost:8000/app
```

**You should see:**
- Beautiful purple gradient header
- "Evolve Consciousness Engine" title
- 5 tabs: Upload, Query, Analysis, Documents, Training Data
- Clean, modern interface

**If the page doesn't load:**
- Check that the server is still running
- Check the server terminal for errors
- Try refreshing the page

### Test 4: Upload a Test Document

**In the browser (Upload tab):**

1. **Title:** `Test Document`
2. **Source:** `Test`
3. **Content:** Paste this test text:

```
Step 1: We admitted we were powerless over alcohol—that our lives had become unmanageable.

This is the foundation of recovery. Powerlessness is not weakness, it's honesty. When we admit our powerlessness, we open the door to a higher power. This connects to the root chakra, which governs our sense of safety and survival. The admission of powerlessness is a consciousness shift from denial (fear_100) to courage (courage_200) on the Hawkins scale.

In quantum physics, the observer effect shows that consciousness affects reality. When we observe our powerlessness honestly, we collapse the wave function of denial and create a new reality of acceptance. This is the beginning of spiritual awakening, similar to moksha in Hinduism or nirvana in Buddhism.
```

4. Click **"Upload Document"**

**Expected result:**
- Success message appears
- Shows "Successfully uploaded X chunks"
- Chunk size: 1800 characters

**In the server terminal, you should see:**
- Embedding generation logs
- Pinecone upsert logs
- No errors

### Test 5: Query the Knowledge Base

**In the browser (Query tab):**

1. **Question:** `How does Step 1 relate to consciousness evolution?`
2. **Number of Sources:** `5`
3. Click **"Ask Question"**

**Expected result:**
- Answer appears (synthesized by Claude)
- Sources section shows the test document
- Relevance score shown (should be high, like 0.85+)

**This tests:**
- Embedding generation ✅
- Pinecone search ✅
- Claude synthesis ✅
- Full RAG pipeline ✅

### Test 6: View Documents

**In the browser (Documents tab):**

1. Click **"Refresh Documents"**

**Expected result:**
- Shows "Test Document"
- Status: "pending" (not analyzed yet)
- Shows chunk count
- Shows upload date

### Test 7: Run Claude Analysis

**In the browser (Analysis tab):**

1. Select **"Individual"** analysis level
2. Click **"Start Analysis"**

**Expected result:**
- Progress bar appears
- Shows "Analyzing document 1 of 1..."
- Progress reaches 100%
- Success message appears
- Statistics show 1 analyzed document

**In the server terminal, you should see:**
- Claude API calls
- Rate limiting pauses (2 seconds)
- Analysis results being saved

### Test 8: View Analysis Results

**In the browser (Documents tab):**

1. Click **"Refresh Documents"**

**Expected result:**
- "Test Document" now shows status: "completed"

**In the browser (Analysis tab):**

**Expected result:**
- Statistics show:
  - Total Documents: 1
  - Analyzed: 1
  - Connections Found: 0 (only 1 doc, so no cross-doc connections yet)

### Test 9: Generate Training Data

**In the browser (Training Data tab):**

1. Click **"Generate Training Data"**

**Expected result:**
- Success message
- Shows number of training pairs created

2. Click **"Export to JSONL"**

**Expected result:**
- File downloads: `evolve-training-data.jsonl`
- Success message shows number of pairs exported

### Test 10: Verify Database

```bash
# In a new terminal (keep server running)
cd backend

# Check that database was created
ls -lh consciousness_rag.db

# Should show a file with size > 0 bytes
```

---

## ✅ Step 5: Full System Test with Real Document

Now that basic tests pass, try with a real document:

### Upload a Real Document

1. **Find a document** (e.g., Big Book Chapter 1, a consciousness article, etc.)
2. **Copy the text** (aim for 2,000-10,000 characters for this test)
3. **Upload via the Upload tab**
4. **Query it** with relevant questions
5. **Run analysis** on it
6. **Generate training data**

### Expected Performance

- **Upload:** 3-5 seconds for a 5,000-character document
- **Query:** 2-3 seconds per question
- **Analysis:** 2 seconds per document (rate-limited)

### Monitor Costs

After this test, check your API usage:

- **OpenAI:** https://platform.openai.com/usage
- **Anthropic:** https://console.anthropic.com/settings/usage

**Expected costs for 1 document:**
- Upload: ~$0.01 (embedding)
- Query (5 questions): ~$0.10 (Claude)
- Analysis: ~$0.01 (Claude)
- **Total: ~$0.12**

---

## 🚀 Step 6: Production Deployment

### Option A: Keep Running Locally

If you just want to use it on your Mac:

1. **Start server when needed:**
   ```bash
   cd ~/Desktop/consciousness-rag/backend
   source venv/bin/activate
   python main_complete.py
   ```

2. **Access at:** `http://localhost:8000/app`

3. **Stop server:** Press `CTRL+C` in the terminal

### Option B: Run as Background Service (Mac)

Create a launch agent to auto-start on login:

```bash
# Create launch agent directory if it doesn't exist
mkdir -p ~/Library/LaunchAgents

# Create launch agent plist
cat > ~/Library/LaunchAgents/com.evolve.consciousness-rag.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.evolve.consciousness-rag</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Users/YOUR_USERNAME/Desktop/consciousness-rag/backend/venv/bin/python</string>
        <string>/Users/YOUR_USERNAME/Desktop/consciousness-rag/backend/main_complete.py</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/Users/YOUR_USERNAME/Desktop/consciousness-rag/backend</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/Users/YOUR_USERNAME/Desktop/consciousness-rag/backend/logs/stdout.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/YOUR_USERNAME/Desktop/consciousness-rag/backend/logs/stderr.log</string>
</dict>
</plist>
EOF

# Replace YOUR_USERNAME with your actual Mac username
sed -i '' "s/YOUR_USERNAME/$(whoami)/g" ~/Library/LaunchAgents/com.evolve.consciousness-rag.plist

# Create logs directory
mkdir -p ~/Desktop/consciousness-rag/backend/logs

# Load the launch agent
launchctl load ~/Library/LaunchAgents/com.evolve.consciousness-rag.plist

# Check status
launchctl list | grep consciousness-rag
```

**Now the server will:**
- Start automatically when you log in
- Restart automatically if it crashes
- Run in the background
- Log to `backend/logs/`

**To stop the service:**
```bash
launchctl unload ~/Library/LaunchAgents/com.evolve.consciousness-rag.plist
```

**To start the service:**
```bash
launchctl load ~/Library/LaunchAgents/com.evolve.consciousness-rag.plist
```

### Option C: Deploy to Cloud (Future)

If you want to access from anywhere:

1. **Digital Ocean Droplet** (4GB RAM minimum)
2. **AWS EC2** (t3.medium or larger)
3. **Google Cloud Compute Engine**

**Note:** Your Mac M1 Max is perfect for this - no need for cloud unless you want remote access.

---

## 📊 Step 7: Monitor Performance

### Check Memory Usage

```bash
# While server is running
ps aux | grep main_complete.py
```

**Expected:** ~200MB RAM usage

### Check Database Size

```bash
cd backend
ls -lh consciousness_rag.db
```

**Expected:** ~10MB per 100 documents

### Check Logs

```bash
# If running as service
tail -f ~/Desktop/consciousness-rag/backend/logs/stdout.log
tail -f ~/Desktop/consciousness-rag/backend/logs/stderr.log
```

---

## 🐛 Troubleshooting

### Server Won't Start

**Error:** `ModuleNotFoundError: No module named 'pinecone'`

**Solution:**
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Pinecone Connection Failed

**Error:** `Pinecone not initialized`

**Solution:**
- Check `PINECONE_API_KEY` in `.env`
- Verify API key is correct at https://app.pinecone.io/

### Claude Query Failed

**Error:** `Claude query failed`

**Solution:**
- Check `ANTHROPIC_API_KEY` in `.env`
- Verify API key is correct at https://console.anthropic.com/

### Database Locked

**Error:** `database is locked`

**Solution:**
- Only one analysis can run at a time
- Wait for current analysis to complete
- Or restart the server

### Frontend Not Loading

**Error:** 404 Not Found

**Solution:**
- Check that `static/index_complete.html` exists
- Restart the server
- Clear browser cache

---

## 📈 Next Steps After Deployment

### 1. Upload Your Document Library

- Start with 10-20 documents
- Test queries to verify quality
- Run analysis on all documents
- Generate training data

### 2. Fine-Tune a Model

Once you have 50+ training pairs:

```bash
# Install OpenAI CLI
pip install openai

# Upload training file
openai api fine_tunes.create \
  -t evolve-training-data.jsonl \
  -m gpt-4o-mini-2024-07-18 \
  --suffix "evolve-consciousness"

# Monitor progress
openai api fine_tunes.follow -i ft-xxxxx

# Once complete, update .env with fine-tuned model ID
```

### 3. Scale Up

- Upload more documents (100s or 1000s)
- Create topic-specific collections
- Build multiple fine-tuned models (Beginner, Intermediate, Advanced)
- Integrate with your NEURORecovery program

---

## ✅ Success Criteria

You'll know the system is working correctly when:

- [ ] Server starts without errors
- [ ] Health check returns all "configured"
- [ ] Frontend loads at http://localhost:8000/app
- [ ] Document uploads successfully (3-5 seconds)
- [ ] Queries return relevant answers (2-3 seconds)
- [ ] Analysis completes without errors
- [ ] Training data exports successfully
- [ ] Memory usage stays under 500MB
- [ ] No API errors in logs

---

## 🎯 Summary

**Total time to deploy:** 30-45 minutes

**Steps:**
1. Clone repo (5 min)
2. Set up Python environment (10 min)
3. Configure API keys (5 min)
4. Test system (15 min)
5. Deploy (5 min)

**You're ready to build your consciousness knowledge base!** 🧠✨

---

## 📞 Need Help?

If you encounter issues:

1. Check the error message carefully
2. Review the troubleshooting section above
3. Check `COMPLETE_DEPLOYMENT_GUIDE.md` for more details
4. Verify all API keys are correct
5. Make sure you're on the `simplified-clean-2024` branch

**The system is production-ready and tested!** 🚀
