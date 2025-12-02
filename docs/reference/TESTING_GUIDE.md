# Evolve Consciousness RAG - Testing Guide

**Platform:** macOS
**Last Updated:** November 30, 2025

---

## Table of Contents

1. [Testing Overview](#testing-overview)
2. [Prerequisites](#prerequisites)
3. [Testing the Upload System](#testing-the-upload-system)
4. [Testing the Query Endpoint](#testing-the-query-endpoint)
5. [Testing MCP Server Connection](#testing-mcp-server-connection)
6. [Sample Test Queries](#sample-test-queries)
7. [Expected Outputs](#expected-outputs)
8. [Performance Benchmarks](#performance-benchmarks)
9. [Troubleshooting Failed Tests](#troubleshooting-failed-tests)

---

## Testing Overview

This guide covers how to test all components of the Evolve Consciousness RAG system:

- **Upload System:** Document ingestion and chunking
- **Query System:** Semantic search and answer generation
- **MCP Integration:** Claude Desktop connectivity
- **End-to-End:** Complete workflows

### Test Types

1. **Smoke Tests** - Quick checks that basic functionality works
2. **Integration Tests** - Verify components work together
3. **End-to-End Tests** - Complete user workflows
4. **Performance Tests** - Speed and efficiency benchmarks

---

## Prerequisites

Before running tests:

### 1. Backend Server Running

Start your backend server in one terminal:

```bash
cd /Users/carriehuff/consciousness-RAG/consciousness-rag/backend
source venv/bin/activate
python main.py
```

Keep this terminal open. You should see:

```
INFO:     All services initialized successfully!
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 2. SSH Tunnel (If Using DigitalOcean)

In another terminal, establish SSH tunnel:

```bash
ssh -L 8000:localhost:8000 root@146.190.169.226
```

Keep this running for remote server access.

### 3. Virtual Environment Activated

For running test scripts:

```bash
cd backend
source venv/bin/activate
```

### 4. API Keys Configured

Verify your `.env` file has all required keys:

```bash
# Check environment variables are loaded
python3 -c "import os; from dotenv import load_dotenv; load_dotenv(); print('Pinecone:', os.getenv('PINECONE_API_KEY')[:10], '...'); print('OpenAI:', os.getenv('OPENAI_API_KEY')[:10], '...'); print('Anthropic:', os.getenv('ANTHROPIC_API_KEY')[:10], '...')"
```

---

## Testing the Upload System

### Test 1: Health Check (Smoke Test)

Verify all services are connected:

```bash
curl http://localhost:8000/health
```

**Expected Output:**

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

**Success Criteria:**
- Status is "healthy"
- All services show connected: true
- No error messages

**If Test Fails:** See [Troubleshooting](#troubleshooting-failed-tests)

---

### Test 2: Simple Text Upload (Integration Test)

Upload a small test document:

```bash
curl -X POST http://localhost:8000/upload \
  -H "Content-Type: application/json" \
  -d '{
    "text": "The First Step is about surrender. When we admit powerlessness, we open the heart chakra and align with quantum consciousness.",
    "title": "Test Document - First Step",
    "source": "test",
    "use_ai_tagging": false
  }'
```

**Expected Output:**

```json
{
  "status": "success",
  "message": "Document 'Test Document - First Step' processed successfully",
  "chunks_created": 1,
  "vectors_uploaded": 1
}
```

**Success Criteria:**
- Status is "success"
- At least 1 chunk created
- Vectors uploaded matches chunks created
- No errors in response

---

### Test 3: Multi-Chunk Document (Integration Test)

Upload a longer document to test chunking:

```bash
curl -X POST http://localhost:8000/upload \
  -H "Content-Type: application/json" \
  -d '{
    "text": "The First Step of recovery is a profound spiritual practice. When we admit powerlessness over addiction, we are actually engaging in a form of surrender that opens the heart chakra. This admission is not weakness - it is the beginning of true strength and consciousness expansion. Modern neuroscience confirms what mystics have known for millennia: the act of surrender activates the prefrontal cortex and reduces activity in the fear-based amygdala. This is the same mechanism described in the Bhagavad Gita as letting go of the fruits of action. The 12 Steps are not just a recovery program - they are an ascension path, a mystical journey that parallels the Kabbalistic Tree of Life, the Buddhist Noble Eightfold Path, and the Hermetic principles of transformation. Each step corresponds to a different level of consciousness on the Hawkins Scale, moving from shame and fear toward courage, acceptance, and ultimately, love and peace.",
    "title": "First Step and Consciousness - Expanded",
    "source": "test-multi-chunk",
    "use_ai_tagging": false
  }'
```

**Expected Output:**

```json
{
  "status": "success",
  "message": "Document 'First Step and Consciousness - Expanded' processed successfully",
  "chunks_created": 1,
  "vectors_uploaded": 1
}
```

**Success Criteria:**
- Multiple chunks created (depends on text length)
- All chunks uploaded successfully
- Check stats endpoint to verify

---

### Test 4: AI-Enhanced Tagging (Advanced Test)

Test AI tagging with Ollama (free, local):

```bash
curl -X POST http://localhost:8000/upload \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Quantum entanglement suggests that consciousness is non-local, existing beyond space and time. This aligns with the Hermetic principle of correspondence - as above, so below.",
    "title": "Quantum Consciousness Test",
    "source": "test-ai-tagging",
    "use_ai_tagging": true,
    "ai_provider": "ollama",
    "ollama_model": "llama3.1"
  }'
```

**Expected Output:**

```json
{
  "status": "success",
  "message": "Document 'Quantum Consciousness Test' processed successfully",
  "chunks_created": 1,
  "vectors_uploaded": 1
}
```

**Success Criteria:**
- Document uploaded successfully
- AI tagging completed (may take 10-30 seconds)
- Enhanced metadata generated

**Note:** Requires Ollama running locally. Install with: `brew install ollama`

---

### Test 5: Check Upload Statistics

Verify documents are in Pinecone:

```bash
curl http://localhost:8000/stats
```

**Expected Output:**

```json
{
  "index_name": "evolve-consciousness",
  "total_vectors": 3,
  "dimension": 1536,
  "namespaces": {}
}
```

**Success Criteria:**
- `total_vectors` > 0 (should match number of uploaded chunks)
- Dimension is 1536
- Index name is correct

---

### Test 6: List Uploaded Documents

Get all documents in the database:

```bash
curl http://localhost:8000/uploaded-documents
```

**Expected Output:**

```json
{
  "status": "success",
  "total_documents": 3,
  "documents": [
    {
      "title": "First Step and Consciousness - Expanded",
      "source": "test-multi-chunk",
      "chunk_count": 1,
      "total_chunks": 1
    },
    {
      "title": "Quantum Consciousness Test",
      "source": "test-ai-tagging",
      "chunk_count": 1,
      "total_chunks": 1
    },
    {
      "title": "Test Document - First Step",
      "source": "test",
      "chunk_count": 1,
      "total_chunks": 1
    }
  ]
}
```

**Success Criteria:**
- Lists all uploaded documents
- Chunk counts are accurate
- Documents sorted alphabetically

---

### Test 7: Duplicate Detection

Check if a document already exists:

```bash
curl -X POST http://localhost:8000/check-duplicate \
  -H "Content-Type: application/json" \
  -d '{"title": "Test Document - First Step"}'
```

**Expected Output:**

```json
{
  "status": "success",
  "exists": true,
  "chunk_count": 1,
  "title": "Test Document - First Step"
}
```

**Success Criteria:**
- Correctly identifies existing documents
- Returns accurate chunk count

---

### Test 8: Delete Document

Remove a test document:

```bash
curl -X DELETE http://localhost:8000/delete-document/Test%20Document%20-%20First%20Step
```

**Expected Output:**

```json
{
  "status": "success",
  "message": "Deleted 1 chunks of 'Test Document - First Step'",
  "chunks_deleted": 1
}
```

**Success Criteria:**
- Document successfully deleted
- Chunk count matches expected

Verify deletion:

```bash
curl http://localhost:8000/stats
# total_vectors should decrease by 1
```

---

### Test 9: Automated Test Suite

Run the built-in test script:

```bash
cd backend
python test_api.py
```

**Expected Output:**

```
============================================================
  EVOLVE CONSCIOUSNESS ENGINE - API TEST
============================================================

✓ Server is online: Evolve Consciousness Engine Online

=== Testing Document Upload ===

✓ Upload successful!
  - Document: The First Step as Spiritual Awakening
  - Chunks created: 2
  - Vectors uploaded: 2

⏳ Waiting for indexing to complete...

=== Testing Query Endpoint ===

✓ Query successful!

📝 Question: How does the First Step relate to consciousness and spirituality?

💡 Answer:
[Detailed answer from Claude...]

📚 Sources used: 2
  1. The First Step as Spiritual Awakening (score: 0.952)
  2. First Step and Consciousness - Expanded (score: 0.847)

=== Database Statistics ===

Index: evolve-consciousness
Total vectors: 2
Dimension: 1536

============================================================
  TEST COMPLETE
============================================================
```

**Success Criteria:**
- All tests pass with ✓ checkmarks
- Upload creates chunks
- Query returns relevant results
- Stats show uploaded vectors

---

## Testing the Query Endpoint

### Test 10: Basic Query (Smoke Test)

Test semantic search and answer generation:

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the First Step about?",
    "top_k": 3
  }'
```

**Expected Output:**

```json
{
  "answer": "The First Step of recovery is fundamentally about surrender and admitting powerlessness over addiction. This act of surrender is not a sign of weakness, but rather the beginning of true strength and consciousness expansion...",
  "sources": [
    {
      "title": "First Step and Consciousness - Expanded",
      "source": "test-multi-chunk",
      "score": 0.952,
      "tags": ["step_1", "heart", "consciousness", "surrender"]
    }
  ],
  "metadata": {
    "matches_found": 1,
    "program_level": "beginner",
    "model": "claude-sonnet-4-5-20250929"
  }
}
```

**Success Criteria:**
- Returns comprehensive answer
- Sources are relevant (high scores > 0.8)
- Metadata includes model and program level
- Answer addresses the question directly

---

### Test 11: Advanced Query with Filters

Query with program level filter:

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How does quantum physics relate to consciousness?",
    "program_level": "advanced",
    "top_k": 5
  }'
```

**Expected Output:**

```json
{
  "answer": "Quantum physics offers profound insights into the nature of consciousness through concepts like entanglement and non-locality...",
  "sources": [
    {
      "title": "Quantum Consciousness Test",
      "source": "test-ai-tagging",
      "score": 0.945,
      "tags": ["quantum_physics", "consciousness", "hermetic"]
    }
  ],
  "metadata": {
    "matches_found": 1,
    "program_level": "advanced",
    "model": "claude-sonnet-4-5-20250929"
  }
}
```

**Success Criteria:**
- Answer tone matches "advanced" program level
- Uses sophisticated language and concepts
- Sources are filtered correctly

---

### Test 12: Empty Results Query

Test query with no matching content:

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Tell me about underwater basket weaving",
    "top_k": 3
  }'
```

**Expected Output:**

```json
{
  "answer": "I couldn't find relevant information in the knowledge base to answer your question. Please try rephrasing or asking about a different topic.",
  "sources": [],
  "metadata": {
    "matches_found": 0
  }
}
```

**Success Criteria:**
- Gracefully handles no matches
- Returns helpful message
- No errors or crashes

---

### Test 13: Performance Test (Query Speed)

Measure query response time:

```bash
time curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Explain the heart chakra",
    "top_k": 5
  }'
```

**Expected Performance:**
- **Total time:** 2-5 seconds
  - Embedding generation: ~0.5 seconds
  - Pinecone search: ~0.5 seconds
  - Claude answer generation: 1-4 seconds

**Success Criteria:**
- Query completes in < 10 seconds
- No timeouts
- Consistent performance across queries

---

## Testing MCP Server Connection

### Test 14: Verify MCP Config

Check Claude Desktop configuration:

```bash
cat ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

**Expected Output:**

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

**Success Criteria:**
- Valid JSON syntax
- Correct file path
- API_URL points to localhost:8000

---

### Test 15: Manual MCP Server Test

Run MCP server manually to check for errors:

```bash
cd /Users/carriehuff/consciousness-RAG/consciousness-rag/mcp-server
python3 server.py
```

**Expected Output:**
- Server starts without errors
- Connects to backend API
- Waits for Claude Desktop commands

**Success Criteria:**
- No Python errors
- No connection refused errors
- Process doesn't crash

Press `Ctrl+C` to stop.

---

### Test 16: Claude Desktop Integration Test

**Prerequisites:** MCP server configured in Claude Desktop

1. Open Claude Desktop
2. Look for tools icon (wrench/tool symbol)
3. Verify "evolveAI" appears in available tools

**Test Query in Claude Desktop:**

```
Can you search the consciousness library for information about surrender?
```

**Expected Behavior:**
- Claude recognizes the query requires evolveAI tool
- Executes query against your Pinecone database
- Returns comprehensive answer with sources

**Success Criteria:**
- Tool executes without errors
- Returns relevant results from your database
- Includes source citations

---

### Test 17: MCP Server Logs

Check for MCP-related errors:

```bash
# View MCP logs
tail -f ~/Library/Logs/Claude/mcp.log

# Or view in Finder
open ~/Library/Logs/Claude/
```

**Success Criteria:**
- No error messages
- Successful connection logs
- Query execution logs appear

---

## Sample Test Queries

### For Testing Basic Functionality

**Query 1: Simple Topic**
```
Question: "What is the First Step?"
Expected: Basic explanation of Step 1 from uploaded content
```

**Query 2: Keyword Search**
```
Question: "Tell me about chakras"
Expected: Information about chakra system from uploaded documents
```

**Query 3: Teacher/Author**
```
Question: "What does Thomas Troward say about consciousness?"
Expected: Quotes and concepts from Troward's work (if uploaded)
```

### For Testing Cross-References

**Query 4: Multiple Traditions**
```
Question: "How do different mystical traditions discuss surrender?"
Expected: Synthesis across multiple traditions in your library
```

**Query 5: Concept Mapping**
```
Question: "Map the 12 steps to the chakra system"
Expected: Connections between steps and chakras
```

**Query 6: Bridge Concepts**
```
Question: "How does quantum physics relate to consciousness?"
Expected: Synthesis of quantum concepts and consciousness
```

### For Testing Metadata Filtering

**Query 7: By Consciousness Level**
```
Question: "Show me content about shame and courage"
Expected: Content tagged with those Hawkins levels
```

**Query 8: By Program Level**
```
Question: "Explain recovery in beginner terms"
Expected: Simple, compassionate language (beginner persona)
```

**Query 9: By Tradition**
```
Question: "What does Kabbalah teach about transformation?"
Expected: Content tagged with Kabbalistic tradition
```

---

## Expected Outputs

### Successful Upload Output

```json
{
  "status": "success",
  "message": "Document '[title]' processed successfully",
  "chunks_created": 5,
  "vectors_uploaded": 5
}
```

### Successful Query Output

```json
{
  "answer": "[Comprehensive answer from Claude...]",
  "sources": [
    {
      "title": "Document Title",
      "source": "filename.pdf",
      "score": 0.95,
      "tags": ["tag1", "tag2", "tag3"]
    }
  ],
  "metadata": {
    "matches_found": 3,
    "program_level": "beginner",
    "model": "claude-sonnet-4-5-20250929"
  }
}
```

### Error Responses

**Connection Error:**
```json
{
  "detail": "Failed to connect to Pinecone"
}
```

**Invalid API Key:**
```json
{
  "detail": "Embedding generation failed: Invalid API key"
}
```

**No Results:**
```json
{
  "answer": "I couldn't find relevant information...",
  "sources": [],
  "metadata": {"matches_found": 0}
}
```

---

## Performance Benchmarks

### Expected Performance Metrics

**Upload Performance:**
- Single chunk: < 2 seconds
- 10 chunks: < 10 seconds
- 100 chunks: < 60 seconds (with batching)
- 300+ chunks: 2-5 minutes (large book)

**Query Performance:**
- Embedding generation: 0.3-0.5 seconds
- Pinecone search: 0.2-0.5 seconds
- Claude answer generation: 1-4 seconds
- **Total:** 2-5 seconds per query

**Batch Processing:**
- Processes 50 chunks at a time
- Each batch: 30-60 seconds
- Prevents timeouts on large uploads

**MCP Server:**
- Response time: Same as query (2-5 seconds)
- Additional overhead: < 0.5 seconds

---

## Troubleshooting Failed Tests

### Upload Tests Failing

**Problem:** Connection refused
```
Solution:
1. Verify backend is running: curl http://localhost:8000/health
2. Check SSH tunnel (if remote): lsof -i :8000
3. Restart backend server
```

**Problem:** Embedding generation fails
```
Solution:
1. Verify OpenAI API key in .env
2. Check OpenAI billing: https://platform.openai.com/account/billing
3. Test API key: python3 -c "from openai import OpenAI; import os; from dotenv import load_dotenv; load_dotenv(); client = OpenAI(api_key=os.getenv('OPENAI_API_KEY')); print('OK')"
```

**Problem:** Encoding errors
```
Solution:
1. System automatically converts to ASCII
2. Check source document encoding
3. Remove special characters manually if needed
```

### Query Tests Failing

**Problem:** No results returned
```
Solution:
1. Verify content uploaded: curl http://localhost:8000/stats
2. Upload test document: python test_api.py
3. Check Pinecone console for vectors
```

**Problem:** Claude API fails
```
Solution:
1. Verify Anthropic API key
2. Check spending cap: curl http://localhost:8000/spending-dashboard
3. Verify billing: https://console.anthropic.com/settings/billing
```

**Problem:** Slow responses
```
Solution:
1. Normal: 2-5 seconds is expected
2. Reduce top_k to 3 instead of 5
3. Check internet connection speed
4. Consider upgrading server if consistently slow
```

### MCP Tests Failing

**Problem:** MCP server not appearing
```
Solution:
1. Verify config file location and syntax
2. Check file path in config is absolute
3. Restart Claude Desktop completely
4. View logs: ~/Library/Logs/Claude/mcp.log
```

**Problem:** Connection refused in MCP
```
Solution:
1. Backend must be running first
2. Verify API_URL in MCP config
3. Test backend: curl http://localhost:8000/health
4. Check SSH tunnel if using remote server
```

**Problem:** MCP crashes
```
Solution:
1. Run server manually to see errors: python3 mcp-server/server.py
2. Check Python version: python3 --version
3. Verify dependencies: pip list
4. Review error logs
```

---

## Testing Checklist

Use this checklist to verify all systems:

### Backend Tests
- [ ] Health check returns "healthy"
- [ ] Upload single document succeeds
- [ ] Upload multi-chunk document succeeds
- [ ] AI tagging completes (if using)
- [ ] Stats show uploaded vectors
- [ ] List documents returns data
- [ ] Duplicate detection works
- [ ] Delete document succeeds

### Query Tests
- [ ] Basic query returns results
- [ ] Advanced query with filters works
- [ ] Empty query handled gracefully
- [ ] Query performance < 10 seconds
- [ ] Sources include relevance scores
- [ ] Answer quality is high

### MCP Tests
- [ ] Config file syntax valid
- [ ] MCP server appears in Claude Desktop
- [ ] Manual server run succeeds
- [ ] Query via Claude Desktop works
- [ ] Sources cited correctly
- [ ] No error logs

### Integration Tests
- [ ] End-to-end upload → query workflow
- [ ] SSH tunnel stable (if remote)
- [ ] Multiple concurrent queries work
- [ ] Large document upload succeeds
- [ ] Spending tracker limits enforced

---

## Next Steps

After completing all tests:

1. **If All Tests Pass:** System is ready for production use
   - Begin uploading your content library
   - Start using Claude Desktop for research
   - Explore advanced queries

2. **If Some Tests Fail:** Review troubleshooting sections
   - Check relevant documentation
   - Verify environment configuration
   - Test components individually

3. **Performance Tuning:**
   - Adjust chunk size if needed
   - Optimize query parameters
   - Monitor API costs

4. **Production Readiness:**
   - Review `DEPLOYMENT_CHECKLIST.md`
   - Set up monitoring
   - Configure backups

---

**Testing Complete!**

You now have comprehensive test coverage for your Evolve Consciousness RAG system. Use this guide regularly to verify system health and troubleshoot issues.
