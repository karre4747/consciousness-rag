# Claude Desktop MCP Setup Guide

**Platform:** macOS
**Claude Desktop Version:** Latest
**MCP Protocol:** Model Context Protocol
**Last Updated:** November 30, 2025

---

## Table of Contents

1. [What is MCP?](#what-is-mcp)
2. [Prerequisites](#prerequisites)
3. [Finding Your Config File](#finding-your-config-file)
4. [MCP Server Configuration](#mcp-server-configuration)
5. [Restarting Claude Desktop](#restarting-claude-desktop)
6. [Verifying Connection](#verifying-connection)
7. [Example Queries](#example-queries)
8. [Troubleshooting](#troubleshooting)

---

## What is MCP?

**Model Context Protocol (MCP)** is a standardized way for Claude Desktop to connect to external tools and data sources. In this setup:

- **Claude Desktop** acts as the client
- **evolveAI MCP Server** acts as the tool provider
- **Pinecone Database** provides the consciousness library data

When you ask Claude a question in Claude Desktop, it can automatically:
1. Query your consciousness library via the MCP server
2. Retrieve relevant content from Pinecone
3. Provide comprehensive answers with source citations

---

## Prerequisites

Before setting up Claude Desktop integration:

1. **Backend Server Running**
   - Your DigitalOcean server should be accessible
   - Or your local backend running on `localhost:8000`
   - Verify with: `curl http://localhost:8000/health`

2. **Claude Desktop Installed**
   - Download from: https://claude.ai/download
   - Install and sign in with your Anthropic account

3. **MCP Server Code** (To be built)
   - The `mcp-server/` directory with `server.py`
   - Python 3.10+ environment for MCP server
   - Note: This guide assumes the MCP server is ready

4. **SSH Tunnel** (If using DigitalOcean)
   - To connect local Claude Desktop to remote server
   - Command: `ssh -L 8000:localhost:8000 root@146.190.169.226`

---

## Finding Your Config File

### macOS Claude Desktop Config Location

The Claude Desktop configuration file is located at:

```
~/Library/Application Support/Claude/claude_desktop_config.json
```

### Opening the Config File

**Option 1: Using Finder (Recommended for beginners)**

1. Open Finder
2. Press `Cmd+Shift+G` (Go to Folder)
3. Paste: `~/Library/Application Support/Claude/`
4. Press Enter
5. Look for `claude_desktop_config.json`
6. Open with TextEdit or your preferred editor

**Option 2: Using Terminal**

```bash
# Create the directory if it doesn't exist
mkdir -p ~/Library/Application\ Support/Claude

# Open in default text editor
open ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Or edit with nano
nano ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Or edit with VS Code
code ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

**Option 3: Using VSCode**

```bash
# Install code command if not available
# In VSCode: Cmd+Shift+P -> "Shell Command: Install 'code' command in PATH"

code ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

### If File Doesn't Exist

If the file doesn't exist yet, create it:

```bash
# Create directory
mkdir -p ~/Library/Application\ Support/Claude

# Create empty config file
touch ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Open for editing
nano ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

---

## MCP Server Configuration

### Basic Configuration Structure

Add this to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "evolveAI": {
      "command": "python3",
      "args": [
        "/Users/carriehuff/consciousness-RAG/consciousness-rag/mcp-server/server.py"
      ],
      "env": {
        "API_URL": "http://localhost:8000"
      }
    }
  }
}
```

### Configuration Explained

**Field Breakdown:**

- `mcpServers`: Root object containing all MCP servers
- `evolveAI`: Name of your MCP server (can be any identifier)
- `command`: Command to run the server (`python3`)
- `args`: Arguments passed to the command (path to `server.py`)
- `env`: Environment variables for the server
  - `API_URL`: Your backend API endpoint

### Important: Update File Paths

**You MUST update the path to match your system:**

```json
"args": [
  "/Users/YOUR_USERNAME/consciousness-RAG/consciousness-rag/mcp-server/server.py"
]
```

To find the correct path:

```bash
# Navigate to your project
cd ~/consciousness-RAG/consciousness-rag/mcp-server

# Get absolute path
pwd

# Copy the output and add /server.py to the end
```

### Remote Server Configuration

If connecting to DigitalOcean (via SSH tunnel):

```json
{
  "mcpServers": {
    "evolveAI": {
      "command": "python3",
      "args": [
        "/Users/carriehuff/consciousness-RAG/consciousness-rag/mcp-server/server.py"
      ],
      "env": {
        "API_URL": "http://localhost:8000"
      }
    }
  }
}
```

**Prerequisite:** SSH tunnel must be running:

```bash
# In a separate terminal window, keep this running
ssh -L 8000:localhost:8000 root@146.190.169.226
```

### Complete Example with Multiple Servers

If you have other MCP servers configured:

```json
{
  "mcpServers": {
    "evolveAI": {
      "command": "python3",
      "args": [
        "/Users/carriehuff/consciousness-RAG/consciousness-rag/mcp-server/server.py"
      ],
      "env": {
        "API_URL": "http://localhost:8000"
      }
    },
    "another-mcp-server": {
      "command": "node",
      "args": ["/path/to/another/server.js"]
    }
  }
}
```

---

## Restarting Claude Desktop

After editing the config file, you MUST restart Claude Desktop for changes to take effect.

### Method 1: Quit and Reopen (Recommended)

1. Click "Claude" in the menu bar
2. Select "Quit Claude" (or press `Cmd+Q`)
3. Wait 3 seconds
4. Open Claude Desktop again from Applications

### Method 2: Force Quit (If Claude is unresponsive)

1. Press `Cmd+Option+Esc`
2. Select "Claude"
3. Click "Force Quit"
4. Reopen Claude Desktop

### Method 3: Terminal

```bash
# Force quit Claude Desktop
pkill -9 "Claude"

# Wait 2 seconds
sleep 2

# Reopen (adjust path if needed)
open -a "Claude"
```

---

## Verifying Connection

### Check MCP Server Status

When Claude Desktop starts with MCP servers configured:

1. Look for the tools icon in Claude Desktop (usually a wrench or tool icon)
2. You should see "evolveAI" listed as an available tool
3. Click on it to see available functions

### Test Connection Manually

Before using Claude Desktop, verify your backend is accessible:

```bash
# Test health endpoint
curl http://localhost:8000/health

# Expected response:
# {
#   "status": "healthy",
#   "pinecone": {"connected": true, ...},
#   ...
# }
```

### Check Claude Desktop Logs

If the MCP server doesn't appear:

```bash
# View Claude Desktop logs
tail -f ~/Library/Logs/Claude/mcp.log

# Or view all logs
open ~/Library/Logs/Claude/
```

Look for errors related to:
- Python execution
- File not found (incorrect path)
- API connection issues

---

## Example Queries

Once connected, you can ask Claude these types of questions:

### Basic Queries

**Query 1: Simple Topic Search**
```
Can you search the consciousness library for information about the First Step in recovery?
```

Expected behavior:
- Claude recognizes this requires the evolveAI tool
- Queries your Pinecone database
- Returns relevant content with sources

**Query 2: Cross-Tradition Research**
```
Using the consciousness library, explain how surrender is discussed across different mystical traditions.
```

**Query 3: Specific Teacher Lookup**
```
Search the library for what Thomas Troward says about consciousness and manifestation.
```

### Advanced Queries

**Query 4: Mapping Concepts**
```
Query the consciousness library to map the 12 steps to the chakra system.
```

**Query 5: Comparative Analysis**
```
Using the library, compare how ego death is described in 12-step recovery versus mystical Dark Night of the Soul experiences.
```

**Query 6: Synthesis Request**
```
Search the consciousness library for connections between quantum physics and consciousness. Synthesize the key themes.
```

### Research-Focused Queries

**Query 7: Course Content Research**
```
I'm creating a lesson on Step 4. Search the library for astrological correspondences and mystical parallels to Step 4.
```

**Query 8: Multi-Source Synthesis**
```
Query the consciousness library for all references to the etheric body across different teachers and traditions.
```

**Query 9: Concept Exploration**
```
Using the consciousness library, find all discussions of the observer effect in quantum physics and its relation to consciousness.
```

### Expected Response Format

Claude will respond with:

1. **Answer:** Comprehensive synthesis of the information
2. **Sources:** Specific documents/chunks retrieved
3. **Citations:** References to authors, books, and page numbers (if available)
4. **Metadata:** Tags, themes, consciousness levels detected

Example:
```
Based on my search of your consciousness library, the First Step relates to surrender across multiple traditions:

**12-Step Recovery:**
[Content from recovery texts...]

**Mystical Traditions:**
[Content from mystical sources...]

**Quantum Physics Parallels:**
[Content from consciousness/physics texts...]

**Sources:**
1. "The First Step as Spiritual Awakening" (Score: 0.95)
2. Thomas Troward - "The Edinburgh Lectures" (Score: 0.89)
3. [Additional sources...]
```

---

## Troubleshooting

### Issue: MCP Server Not Appearing in Claude Desktop

**Symptoms:** No tools icon, or evolveAI not listed

**Solutions:**

1. **Verify Config File Location**
   ```bash
   ls -la ~/Library/Application\ Support/Claude/claude_desktop_config.json
   ```

2. **Check JSON Syntax**
   ```bash
   # Validate JSON syntax
   python3 -m json.tool ~/Library/Application\ Support/Claude/claude_desktop_config.json
   ```

   If this returns an error, you have invalid JSON syntax.

3. **Verify File Path in Config**
   ```bash
   # Check if server.py exists at the path specified
   ls -la /Users/carriehuff/consciousness-RAG/consciousness-rag/mcp-server/server.py
   ```

4. **Check Python Path**
   ```bash
   which python3
   # Should return something like /usr/bin/python3
   ```

5. **Restart Claude Desktop Completely**
   - Quit Claude Desktop
   - Wait 5 seconds
   - Reopen

### Issue: Connection Refused or Timeout

**Symptoms:** MCP server appears but queries fail with connection errors

**Solutions:**

1. **Verify Backend is Running**
   ```bash
   curl http://localhost:8000/health
   ```

2. **Check SSH Tunnel (If using DigitalOcean)**
   ```bash
   # Verify tunnel is active
   lsof -i :8000

   # If not running, start it
   ssh -L 8000:localhost:8000 root@146.190.169.226
   ```

3. **Test API Directly**
   ```bash
   curl -X POST http://localhost:8000/query \
     -H "Content-Type: application/json" \
     -d '{"question": "test", "top_k": 1}'
   ```

4. **Check Firewall Settings**
   - Ensure macOS firewall allows localhost connections
   - System Preferences > Security & Privacy > Firewall

### Issue: MCP Server Starts but Returns Errors

**Symptoms:** Tool executes but returns error messages

**Solutions:**

1. **Check MCP Server Logs**
   ```bash
   # View recent logs
   tail -f ~/Library/Logs/Claude/mcp.log
   ```

2. **Verify API_URL Environment Variable**
   - Should be `http://localhost:8000`
   - No trailing slash
   - Correct protocol (http not https for localhost)

3. **Test Query Endpoint Manually**
   ```bash
   curl -X POST http://localhost:8000/query \
     -H "Content-Type: application/json" \
     -d '{
       "question": "test consciousness",
       "top_k": 3
     }'
   ```

4. **Check Pinecone Connection**
   ```bash
   # Verify backend has data
   curl http://localhost:8000/stats

   # Should show total_vectors > 0
   ```

### Issue: Permission Denied Errors

**Symptoms:** `Permission denied` when Claude tries to run MCP server

**Solutions:**

1. **Make server.py Executable**
   ```bash
   chmod +x /Users/carriehuff/consciousness-RAG/consciousness-rag/mcp-server/server.py
   ```

2. **Check File Ownership**
   ```bash
   ls -la /Users/carriehuff/consciousness-RAG/consciousness-rag/mcp-server/server.py

   # Should be owned by your user
   # If not, fix it:
   sudo chown $USER /Users/carriehuff/consciousness-RAG/consciousness-rag/mcp-server/server.py
   ```

3. **Verify Python Permissions**
   ```bash
   which python3
   ls -la $(which python3)
   ```

### Issue: MCP Server Crashes or Stops Responding

**Symptoms:** Initially works, then stops responding

**Solutions:**

1. **Check for Python Errors**
   ```bash
   # Run server manually to see errors
   python3 /Users/carriehuff/consciousness-RAG/consciousness-rag/mcp-server/server.py
   ```

2. **Verify Dependencies Installed**
   ```bash
   cd /Users/carriehuff/consciousness-RAG/consciousness-rag/mcp-server
   pip list | grep -E "requests|anthropic"
   ```

3. **Check Backend Server Status**
   ```bash
   curl http://localhost:8000/health
   ```

4. **Restart Everything**
   ```bash
   # 1. Stop backend server (Ctrl+C in that terminal)
   # 2. Quit Claude Desktop
   # 3. Start backend server
   python3 main.py
   # 4. Start Claude Desktop
   open -a "Claude"
   ```

### Issue: Queries Return Empty Results

**Symptoms:** MCP works but returns "No results found"

**Solutions:**

1. **Verify Content is Uploaded**
   ```bash
   curl http://localhost:8000/stats

   # Check that total_vectors > 0
   ```

2. **Upload Test Content**
   ```bash
   cd backend
   python test_api.py
   ```

3. **Check Query is Reaching Backend**
   - Look at backend server logs
   - Should see "Processing query: [your question]"

4. **Verify Pinecone Index Has Data**
   - Log in to Pinecone console
   - Check index statistics
   - Verify vectors exist

### Getting More Help

If issues persist:

1. **Check Backend Logs**
   - Look at the terminal where `python main.py` is running
   - Errors will appear there

2. **Check Claude Desktop Logs**
   ```bash
   open ~/Library/Logs/Claude/
   ```

3. **Test API Directly**
   - Use `test_api.py` to verify backend works
   - If backend works but MCP doesn't, issue is in MCP server

4. **Review Documentation**
   - `INSTALLATION.md` - Backend setup
   - `TESTING_GUIDE.md` - Comprehensive testing
   - `TROUBLESHOOTING.md` - Detailed debugging

---

## Configuration Checklist

Use this to verify your setup:

- [ ] Claude Desktop installed and signed in
- [ ] Backend server running (`http://localhost:8000/health` returns "healthy")
- [ ] SSH tunnel active (if using DigitalOcean)
- [ ] Config file created at correct location
- [ ] JSON syntax valid (no commas, brackets errors)
- [ ] File path in config is absolute and correct
- [ ] `server.py` exists and is executable
- [ ] Claude Desktop restarted after config changes
- [ ] evolveAI tool appears in Claude Desktop
- [ ] Test query returns results

---

## Next Steps

Once Claude Desktop is connected:

1. **Read the Coding Guide** ⭐ **IMPORTANT**
   - See `CLAUDE_CODING_GUIDE.md` for explicit instructions when working on the codebase
   - This guide tells Claude Desktop how to follow the development plan and maintain code quality
   - Essential reading before making any code changes

2. **Upload Your Content**
   - Use the web interface at `http://localhost:8000`
   - Or use `ingest_content.py` for batch uploads

3. **Start Researching**
   - Ask Claude questions about your consciousness library
   - Use for course content creation
   - Explore connections across traditions

4. **Review Testing Guide**
   - See `TESTING_GUIDE.md` for comprehensive test scenarios
   - Learn advanced query techniques

---

**MCP Setup Complete!**

You can now use Claude Desktop as a natural language interface to your entire consciousness library. Ask questions, explore connections, and create course content with comprehensive research at your fingertips.
