# Evolve Consciousness RAG - Installation Guide

**Platform:** macOS
**Python Version:** 3.10+
**Last Updated:** November 30, 2025

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [System Requirements](#system-requirements)
3. [Step-by-Step Installation](#step-by-step-installation)
4. [Environment Configuration](#environment-configuration)
5. [Pinecone Setup](#pinecone-setup)
6. [API Key Configuration](#api-key-configuration)
7. [Testing Your Installation](#testing-your-installation)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before you begin, ensure you have the following:

### Required Accounts & API Keys

1. **Pinecone Account** (Vector Database)
   - Sign up at: https://www.pinecone.io/
   - Free tier: 100K vectors (sufficient for testing)
   - Get your API key from the Pinecone console

2. **OpenAI Account** (Embeddings)
   - Sign up at: https://platform.openai.com/
   - Add billing information
   - Generate an API key
   - Cost: ~$0.13 per 1M tokens (very affordable)

3. **Anthropic Account** (Claude AI)
   - Sign up at: https://console.anthropic.com/
   - Add billing information
   - Generate an API key
   - Cost: $3 per 1M input tokens, $15 per 1M output tokens

### System Tools

- **Python 3.10 or higher**
- **pip** (Python package installer)
- **Git** (for cloning the repository)
- **Terminal** access
- **Claude Desktop** (for MCP integration - separate setup)

---

## System Requirements

### macOS Specifications

- **OS:** macOS 10.15 (Catalina) or later
- **RAM:** 4GB minimum, 8GB recommended
- **Disk Space:** 2GB for dependencies and virtual environment
- **Internet:** Stable connection required for API calls

### Python Version Check

Open Terminal and verify your Python installation:

```bash
python3 --version
```

Expected output: `Python 3.10.x` or higher

If Python is not installed or version is too old:

```bash
# Install Python using Homebrew
brew install python@3.11
```

---

## Step-by-Step Installation

### 1. Clone the Repository

Open Terminal and navigate to your preferred directory:

```bash
cd ~/Documents
git clone https://github.com/YOUR_USERNAME/consciousness-RAG.git
cd consciousness-RAG/consciousness-rag
```

Or if you have the files locally, navigate to the project directory:

```bash
cd /Users/carriehuff/consciousness-RAG/consciousness-rag
```

### 2. Create Virtual Environment

A virtual environment keeps your project dependencies isolated:

```bash
# Navigate to the backend directory
cd backend

# Create virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate
```

You should see `(venv)` appear at the start of your terminal prompt.

**Important:** Always activate the virtual environment before running the application:

```bash
source venv/bin/activate
```

To deactivate when you're done:

```bash
deactivate
```

### 3. Install Dependencies

With the virtual environment activated:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This installs:
- FastAPI (web framework)
- Uvicorn (ASGI server)
- Pinecone SDK (vector database)
- OpenAI SDK (embeddings)
- Anthropic SDK (Claude AI)
- tiktoken (token counting)
- python-dotenv (environment variables)
- And other supporting libraries

Expected installation time: 2-5 minutes

### 4. Verify Installation

Check that key packages are installed:

```bash
python3 -c "import fastapi, pinecone, openai, anthropic; print('All packages installed successfully!')"
```

Expected output: `All packages installed successfully!`

---

## Environment Configuration

### 1. Create Environment File

The `.env` file stores your API keys and configuration securely.

```bash
# From the backend directory
cp .env.example .env
```

If `.env.example` doesn't exist, create `.env` manually:

```bash
nano .env
```

### 2. Configure Environment Variables

Edit `.env` with your favorite text editor (nano, vim, VSCode, etc.):

```bash
nano .env
```

Add the following configuration:

```env
# API Keys
PINECONE_API_KEY=your_pinecone_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Pinecone Configuration
PINECONE_INDEX_NAME=evolve-consciousness
PINECONE_DIMENSION=1536

# Model Configuration
EMBEDDING_MODEL=text-embedding-3-large
CLAUDE_MODEL=claude-sonnet-4-5-20250929

# Application Configuration
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```

Save and exit:
- In nano: Press `Ctrl+X`, then `Y`, then `Enter`
- In vim: Press `Esc`, type `:wq`, press `Enter`

### 3. Secure Your Environment File

Ensure `.env` is NOT committed to Git:

```bash
# Check if .gitignore includes .env
grep ".env" ../.gitignore
```

If not found, add it:

```bash
echo ".env" >> ../.gitignore
```

---

## Pinecone Setup

### 1. Create Pinecone Account

1. Go to https://www.pinecone.io/
2. Sign up for a free account
3. Verify your email

### 2. Get Your API Key

1. Log in to Pinecone console
2. Navigate to "API Keys" in the left sidebar
3. Copy your API key
4. Paste it into your `.env` file as `PINECONE_API_KEY`

### 3. Create Index (Automatic)

The application will automatically create the Pinecone index on first run. You don't need to do anything manually.

If you prefer to create it manually:

1. Go to Pinecone console
2. Click "Create Index"
3. Configuration:
   - **Name:** `evolve-consciousness`
   - **Dimensions:** `1536`
   - **Metric:** `cosine`
   - **Region:** `us-east-1` (AWS)
4. Click "Create Index"

---

## API Key Configuration

### OpenAI API Key

1. Go to https://platform.openai.com/
2. Sign up or log in
3. Navigate to API Keys section
4. Click "Create new secret key"
5. Copy the key immediately (you won't see it again)
6. Add to `.env` as `OPENAI_API_KEY`

**Billing Setup:**
- Go to Billing section
- Add payment method
- Set usage limits (recommended: $10/month for testing)

### Anthropic API Key

1. Go to https://console.anthropic.com/
2. Sign up or log in
3. Navigate to API Keys
4. Generate new key
5. Copy the key
6. Add to `.env` as `ANTHROPIC_API_KEY`

**Billing Setup:**
- Go to Billing section
- Add payment method
- The system enforces a $20/month cap by default (configurable)

---

## Testing Your Installation

### 1. Start the Backend Server

With virtual environment activated:

```bash
cd backend
python main.py
```

Expected output:

```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Initializing Pinecone...
INFO:     Connected to Pinecone index: evolve-consciousness
INFO:     Initializing OpenAI client...
INFO:     Initializing Anthropic client...
INFO:     All services initialized successfully!
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

**Keep this terminal window open.** The server must be running for API calls to work.

### 2. Test Health Endpoint

Open a new terminal window and run:

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{
  "status": "healthy",
  "pinecone": {
    "connected": true,
    "index": "evolve-consciousness",
    "total_vectors": 0,
    "dimension": 1536
  },
  "openai": {"connected": true},
  "anthropic": {"connected": true}
}
```

### 3. Run Test Suite

With the server running (in another terminal):

```bash
cd backend
source venv/bin/activate
python test_api.py
```

This will:
1. Upload a test document
2. Query the knowledge base
3. Display results

Expected output:

```
=== Testing Document Upload ===
✓ Upload successful!
  - Document: The First Step as Spiritual Awakening
  - Chunks created: 2
  - Vectors uploaded: 2

=== Testing Query Endpoint ===
✓ Query successful!

Question: How does the First Step relate to consciousness and spirituality?

Answer:
[Detailed answer from Claude...]

Sources used: 2
  1. The First Step as Spiritual Awakening (score: 0.952)
```

### 4. Test Upload Interface

Open your web browser and go to:

```
http://localhost:8000
```

You should see the upload interface where you can:
- Upload documents via drag-and-drop
- View uploaded documents
- Delete documents
- Check for duplicates

---

## Troubleshooting

### Issue: Python version too old

**Error:** `python3: command not found` or version < 3.10

**Solution:**
```bash
# Install Python 3.11 using Homebrew
brew install python@3.11

# Use python3.11 instead of python3
python3.11 -m venv venv
```

### Issue: pip install fails

**Error:** `ERROR: Could not find a version that satisfies the requirement...`

**Solution:**
```bash
# Upgrade pip
pip install --upgrade pip

# Try installing dependencies again
pip install -r requirements.txt
```

### Issue: Pinecone connection fails

**Error:** `Failed to connect to Pinecone` or `Invalid API key`

**Solution:**
1. Verify API key in `.env` has no extra spaces or quotes
2. Check Pinecone console to ensure key is valid
3. Verify you have an active index created
4. Check internet connection

```bash
# Test Pinecone connection
python3 -c "from pinecone import Pinecone; import os; from dotenv import load_dotenv; load_dotenv(); pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY')); print('Connected!'); print(pc.list_indexes())"
```

### Issue: OpenAI embedding fails

**Error:** `OpenAI API key invalid` or `Rate limit exceeded`

**Solution:**
1. Verify API key in `.env`
2. Check billing is set up on OpenAI platform
3. Verify you haven't exceeded rate limits
4. Add usage limits in OpenAI billing settings

### Issue: Claude API fails

**Error:** `Anthropic API key invalid` or `Insufficient credits`

**Solution:**
1. Verify API key in `.env`
2. Check billing is configured
3. Verify spending cap hasn't been reached
4. Check spending dashboard: `curl http://localhost:8000/spending-dashboard`

### Issue: Port 8000 already in use

**Error:** `Error: [Errno 48] Address already in use`

**Solution:**
```bash
# Find process using port 8000
lsof -i :8000

# Kill the process (replace PID with actual process ID)
kill -9 PID

# Or use a different port
uvicorn main:app --host 0.0.0.0 --port 8001
```

### Issue: Module not found errors

**Error:** `ModuleNotFoundError: No module named 'fastapi'`

**Solution:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Verify activation (should see (venv) in prompt)
which python

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: Permission denied errors

**Error:** `Permission denied` when creating virtual environment

**Solution:**
```bash
# Check directory permissions
ls -la

# Change ownership if needed
sudo chown -R $USER:staff .

# Try creating venv again
python3 -m venv venv
```

### Issue: Environment variables not loading

**Error:** `.env` file exists but variables are not loaded

**Solution:**
1. Verify `.env` is in the `backend` directory
2. Check file has no syntax errors
3. Ensure no quotes around values unless needed
4. Restart the server after editing `.env`

```bash
# Verify .env is being loaded
python3 -c "from dotenv import load_dotenv; import os; load_dotenv(); print('Pinecone:', os.getenv('PINECONE_API_KEY')[:8])"
```

### Issue: Encoding errors when uploading

**Error:** `UnicodeEncodeError` or `Character encoding issues`

**Solution:**
The system automatically converts text to ASCII-safe characters. If you still encounter errors:

1. Check source document encoding
2. Try saving document as UTF-8
3. Remove special characters manually
4. The system will strip problematic characters automatically

### Getting Additional Help

If you encounter issues not covered here:

1. Check the logs when running `python main.py`
2. Review `TROUBLESHOOTING.md` for more detailed debugging
3. Check GitHub Issues for known problems
4. Review the API reference in `API_REFERENCE.md`

---

## Next Steps

Once installation is complete:

1. **Upload Content:** See `CLAUDE_DESKTOP_SETUP.md` for MCP integration
2. **Configure Claude Desktop:** Follow the Claude Desktop setup guide
3. **Test Queries:** Use the testing guide to verify everything works
4. **Start Using:** Begin uploading your consciousness and recovery content

---

## Installation Checklist

Use this checklist to verify your installation:

- [ ] Python 3.10+ installed
- [ ] Virtual environment created and activated
- [ ] All dependencies installed via pip
- [ ] `.env` file created with all API keys
- [ ] Pinecone account created and API key configured
- [ ] OpenAI account created and API key configured
- [ ] Anthropic account created and API key configured
- [ ] Server starts without errors
- [ ] `/health` endpoint returns "healthy"
- [ ] Test upload successful
- [ ] Test query returns results
- [ ] Upload interface accessible at http://localhost:8000

---

**Installation Complete!**

You now have a fully functional Evolve Consciousness RAG system running locally on your Mac. Proceed to `CLAUDE_DESKTOP_SETUP.md` to integrate with Claude Desktop.
