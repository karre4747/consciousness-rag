# Evolve Consciousness Engine - API Reference

**Base URL:** `http://146.190.169.226:8000`
**Version:** 1.0.0
**Last Updated:** November 30, 2025

---

## Table of Contents

- [Authentication](#authentication)
- [Rate Limiting](#rate-limiting)
- [Error Handling](#error-handling)
- [Endpoints](#endpoints)
  - [Health & Status](#health--status)
  - [Document Management](#document-management)
  - [Query & Search](#query--search)
  - [Spending & Analytics](#spending--analytics)
- [Data Models](#data-models)
- [Examples](#examples)

---

## Authentication

**Current Status:** No authentication required

The API currently runs without authentication. For production deployment, implement one of:
- API key authentication via headers
- JWT token-based auth
- OAuth 2.0 integration

**Future Implementation:**
```http
Authorization: Bearer YOUR_API_KEY
```

---

## Rate Limiting

**Current Status:** No hard rate limits enforced

**Recommendations:**
- Upload endpoint: Max 10 requests/minute (large documents can take 30-60s)
- Query endpoint: Max 30 requests/minute
- Spending dashboard: Max 60 requests/minute

**Future Headers:**
```http
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 7
X-RateLimit-Reset: 1701363600
```

---

## Error Handling

### Standard Error Response

```json
{
  "detail": "Error message describing what went wrong"
}
```

### HTTP Status Codes

| Code | Meaning | When It Occurs |
|------|---------|----------------|
| 200 | Success | Request completed successfully |
| 400 | Bad Request | Invalid request body or parameters |
| 404 | Not Found | Document or resource doesn't exist |
| 500 | Internal Server Error | Server-side error (API keys, Pinecone, etc.) |
| 503 | Service Unavailable | Database or external service down |

### Common Error Scenarios

**Pinecone Connection Error:**
```json
{
  "detail": "Embedding generation failed: API key invalid"
}
```

**Document Not Found:**
```json
{
  "detail": "No chunks found for 'Document Title'"
}
```

**Upload Timeout:**
```json
{
  "detail": "Upload failed: Request timeout after 120s"
}
```

---

## Endpoints

### Health & Status

#### `GET /`
**Description:** Root endpoint - serves the upload interface (HTML page)

**Response:**
```html
<!DOCTYPE html>
<!-- Upload interface HTML -->
```

**Use Case:** Access web-based upload interface via browser

---

#### `GET /api`
**Description:** Quick API status check

**Response:**
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

**Status Codes:**
- `200 OK` - API is running
- `500 Internal Server Error` - Critical service unavailable

---

#### `GET /health`
**Description:** Detailed health check with database statistics

**Response:**
```json
{
  "status": "healthy",
  "pinecone": {
    "connected": true,
    "index": "evolve-consciousness",
    "total_vectors": 1247,
    "dimension": 1536
  },
  "openai": {
    "connected": true
  },
  "anthropic": {
    "connected": true
  }
}
```

**Error Response:**
```json
{
  "status": "unhealthy",
  "error": "Failed to connect to Pinecone: Invalid API key"
}
```

**Use Case:** Monitor service health, check vector count, verify all services are connected

---

#### `GET /stats`
**Description:** Get Pinecone database statistics

**Response:**
```json
{
  "index_name": "evolve-consciousness",
  "total_vectors": 1247,
  "dimension": 1536,
  "namespaces": {
    "": {
      "vector_count": 1247
    }
  }
}
```

**Use Case:** Check how many document chunks are stored, verify database state

---

### Document Management

#### `POST /upload`
**Description:** Upload and process a document for ingestion into the vector database

**Request Body:**
```json
{
  "text": "Document content here. Can be very long - will be automatically chunked.",
  "title": "Document Title",
  "source": "path/to/document.md",
  "use_ai_tagging": false,
  "ai_provider": "ollama",
  "ollama_model": "llama3.1"
}
```

**Request Parameters:**

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `text` | string | Yes | - | Full document text (any length) |
| `title` | string | Yes | - | Document title (used for identification) |
| `source` | string | No | "unknown" | Source identifier (file path, URL, etc.) |
| `use_ai_tagging` | boolean | No | false | Enable AI-enhanced tagging (slower) |
| `ai_provider` | string | No | "ollama" | AI provider: "ollama" (free) or "openai" (paid) |
| `ollama_model` | string | No | "llama3.1" | Ollama model to use if ai_provider="ollama" |

**Response:**
```json
{
  "status": "success",
  "message": "Document 'Document Title' processed successfully",
  "chunks_created": 47,
  "vectors_uploaded": 47
}
```

**Error Response:**
```json
{
  "detail": "Upload failed: text field is required"
}
```

**Processing Details:**
1. Text is split into ~1000 token chunks with 200 token overlap
2. Each chunk gets an OpenAI embedding (1536 dimensions)
3. Metadata tags are generated (keyword-based or AI-enhanced)
4. Chunks are uploaded to Pinecone in batches of 50

**Tagging Modes:**

**Keyword-Based (Free, Fast):**
```json
{
  "use_ai_tagging": false
}
```
- Uses pattern matching
- Instant results
- Good for bulk uploads

**AI-Enhanced (Paid/Free depending on provider):**
```json
{
  "use_ai_tagging": true,
  "ai_provider": "ollama"
}
```
- Semantic understanding
- More accurate categorization
- Ollama: Free, requires local server
- OpenAI: ~$0.40 per 1000 docs

**Example - Minimum Upload:**
```bash
curl -X POST http://146.190.169.226:8000/upload \
  -H "Content-Type: application/json" \
  -d '{
    "text": "The heart chakra opens through forgiveness...",
    "title": "Heart Chakra Healing"
  }'
```

**Example - Full Upload with AI:**
```bash
curl -X POST http://146.190.169.226:8000/upload \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Long document text here...",
    "title": "Advanced Quantum Consciousness",
    "source": "/content/advanced/quantum_mind.md",
    "use_ai_tagging": true,
    "ai_provider": "ollama",
    "ollama_model": "llama3.1"
  }'
```

**Timeout:** 120 seconds (large documents may take 30-90s)

---

#### `GET /uploaded-documents`
**Description:** Get list of all unique documents in the database

**Response:**
```json
{
  "status": "success",
  "total_documents": 23,
  "documents": [
    {
      "title": "12 Steps and Consciousness",
      "source": "/content/beginner/12_steps.md",
      "chunk_count": 47,
      "total_chunks": 47
    },
    {
      "title": "Advanced Hermetic Principles",
      "source": "/content/advanced/hermeticism.md",
      "chunk_count": 82,
      "total_chunks": 82
    }
  ]
}
```

**Response Fields:**
- `total_documents` - Number of unique documents
- `documents` - Array of document objects
  - `title` - Document title
  - `source` - Source path/identifier
  - `chunk_count` - Number of chunks retrieved (max 10,000)
  - `total_chunks` - Total chunks when uploaded

**Note:** Pinecone query limit is 10,000 vectors, so very large databases may not return all documents

**Use Case:**
- View what's in your database
- Check if a document was uploaded
- Audit your content library

---

#### `POST /check-duplicate`
**Description:** Check if a document with this title already exists

**Request Body:**
```json
{
  "title": "Document Title"
}
```

**Response - Document Exists:**
```json
{
  "status": "success",
  "exists": true,
  "chunk_count": 47,
  "title": "Document Title"
}
```

**Response - Document Not Found:**
```json
{
  "status": "success",
  "exists": false,
  "chunk_count": 0,
  "title": "Document Title"
}
```

**Use Case:**
- Prevent duplicate uploads
- Check if document was successfully uploaded
- Verify document before deletion

**Example:**
```bash
curl -X POST http://146.190.169.226:8000/check-duplicate \
  -H "Content-Type: application/json" \
  -d '{"title": "Heart Chakra Healing"}'
```

---

#### `DELETE /delete-document/{title}`
**Description:** Delete all chunks of a document from Pinecone

**URL Parameter:**
- `title` - Document title (URL-encoded if contains spaces)

**Response:**
```json
{
  "status": "success",
  "message": "Deleted 47 chunks of 'Document Title'",
  "chunks_deleted": 47
}
```

**Response - Not Found:**
```json
{
  "status": "success",
  "message": "No chunks found for 'Document Title'",
  "chunks_deleted": 0
}
```

**Examples:**

**Simple Title:**
```bash
curl -X DELETE http://146.190.169.226:8000/delete-document/Simple
```

**Title with Spaces:**
```bash
curl -X DELETE http://146.190.169.226:8000/delete-document/Heart%20Chakra%20Healing
```

**Python:**
```python
import requests
import urllib.parse

title = "Heart Chakra Healing"
encoded_title = urllib.parse.quote(title)
response = requests.delete(f"http://146.190.169.226:8000/delete-document/{encoded_title}")
```

**Warning:** This operation is permanent and cannot be undone. Always use `/check-duplicate` first to verify what you're deleting.

---

### Query & Search

#### `POST /query`
**Description:** Query the knowledge base using RAG (Retrieval-Augmented Generation)

**Request Body:**
```json
{
  "question": "How does the heart chakra relate to forgiveness?",
  "program_level": "beginner",
  "filters": {
    "primary_chakra": "heart",
    "tradition": "vedic"
  },
  "top_k": 5
}
```

**Request Parameters:**

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `question` | string | Yes | - | User's question |
| `program_level` | string | No | "beginner" | Response tone: "beginner", "intermediate", "advanced" |
| `filters` | object | No | {} | Metadata filters (see [Metadata Schema](METADATA_SCHEMA.md)) |
| `top_k` | integer | No | 5 | Number of similar chunks to retrieve (1-20) |

**Response:**
```json
{
  "answer": "The heart chakra, or Anahata in Sanskrit, is deeply connected to forgiveness as both a spiritual practice and an energetic reality. When we hold resentment or unforgiveness, we create blockages in this energy center...\n\n[Comprehensive answer from Claude continues...]",
  "sources": [
    {
      "title": "Heart Chakra Healing",
      "source": "/content/intermediate/chakras.md",
      "score": 0.892,
      "tags": ["heart", "anahata", "forgiveness", "healing"]
    },
    {
      "title": "Emotional Release Techniques",
      "source": "/content/beginner/emotions.md",
      "score": 0.856,
      "tags": ["emotions", "healing", "heart"]
    }
  ],
  "metadata": {
    "matches_found": 5,
    "program_level": "beginner",
    "model": "claude-sonnet-4-5-20250929"
  }
}
```

**Response Fields:**
- `answer` - Claude's comprehensive answer (500-2000 tokens)
- `sources` - Array of source documents used
  - `title` - Document title
  - `source` - Source path
  - `score` - Similarity score (0-1, higher is better)
  - `tags` - Document tags
- `metadata` - Query metadata
  - `matches_found` - Number of chunks found
  - `program_level` - Tone used for response
  - `model` - Claude model used

**Program Level Personas:**

**Beginner:**
- Simple language
- Relatable examples
- Hope and practical steps
- Gentle, compassionate tone

**Intermediate:**
- Science and spirituality
- Neuroscience + quantum concepts
- Mystical traditions
- Clarity and depth

**Advanced:**
- Esoteric wisdom
- Quantum physics
- Consciousness studies
- Precision and profound insight

**No Results:**
```json
{
  "answer": "I couldn't find relevant information in the knowledge base to answer your question. Please try rephrasing or asking about a different topic.",
  "sources": [],
  "metadata": {
    "matches_found": 0
  }
}
```

**Example Queries:**

**Basic Query:**
```bash
curl -X POST http://146.190.169.226:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the first step in recovery?",
    "program_level": "beginner"
  }'
```

**Advanced Query with Filters:**
```bash
curl -X POST http://146.190.169.226:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Explain photon consciousness and chakras",
    "program_level": "advanced",
    "filters": {
      "bridge_concept": "photon_consciousness",
      "all_chakras": {"$in": ["crown", "third_eye"]}
    },
    "top_k": 10
  }'
```

**Filter by Teacher:**
```bash
curl -X POST http://146.190.169.226:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What did Blavatsky teach about consciousness?",
    "filters": {
      "teacher": "blavatsky"
    }
  }'
```

**See [METADATA_SCHEMA.md](METADATA_SCHEMA.md) for complete filtering guide.**

---

### Spending & Analytics

#### `GET /spending-dashboard`
**Description:** Get Claude API spending statistics and history

**Query Parameters:**
- `month` (optional) - Format: "2025-11" (defaults to current month)

**Response:**
```json
{
  "status": "success",
  "stats": {
    "month": "2025-11",
    "analysis_count": 12,
    "total_documents_analyzed": 847,
    "total_input_tokens": 423891,
    "total_output_tokens": 15672,
    "total_cost": 12.74,
    "monthly_cap": 20.0,
    "estimated_pages_analyzed": 651,
    "remaining_budget": 7.26,
    "budget_used_percentage": 63.7
  },
  "history": [
    {
      "timestamp": "2025-11-30 14:23:45",
      "analysis_type": "theme",
      "document_count": 156,
      "input_tokens": 89234,
      "output_tokens": 2341,
      "total_cost": 2.71
    },
    {
      "timestamp": "2025-11-29 09:15:22",
      "analysis_type": "recent",
      "document_count": 50,
      "input_tokens": 23456,
      "output_tokens": 876,
      "total_cost": 0.72
    }
  ]
}
```

**Stats Fields:**
- `month` - Month being queried
- `analysis_count` - Number of Claude analyses run
- `total_documents_analyzed` - Total document chunks analyzed
- `total_input_tokens` - Total input tokens sent to Claude
- `total_output_tokens` - Total output tokens from Claude
- `total_cost` - Total cost in USD
- `monthly_cap` - Spending limit for the month
- `estimated_pages_analyzed` - Rough page count (650 tokens = 1 page)
- `remaining_budget` - How much budget is left
- `budget_used_percentage` - Percentage of budget used

**Example:**
```bash
# Current month
curl http://146.190.169.226:8000/spending-dashboard

# Specific month
curl http://146.190.169.226:8000/spending-dashboard?month=2025-10
```

**Use Case:**
- Monitor Claude API costs
- Track usage over time
- Plan budget for content analysis

---

#### `POST /update-spending-cap`
**Description:** Update monthly spending cap

**Request Body:**
```json
{
  "new_cap": 40.00
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Monthly cap updated to $40.0",
  "new_cap": 40.0
}
```

**Error - Invalid Cap:**
```json
{
  "detail": "Cap must be a positive number"
}
```

**Example:**
```bash
curl -X POST http://146.190.169.226:8000/update-spending-cap \
  -H "Content-Type: application/json" \
  -d '{"new_cap": 40.00}'
```

**Note:** Cap applies to current month. Each month starts with the default cap ($20) unless updated.

---

#### `POST /estimate-analysis-cost`
**Description:** Calculate cost BEFORE running Claude analysis

**Request Body:**
```json
{
  "analysis_type": "recent",
  "limit": 50,
  "filters": {}
}
```

**Request Parameters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `analysis_type` | string | Yes | "recent", "full", or "theme" |
| `limit` | integer | No | Number of documents (for "recent" type) |
| `filters` | object | No | Metadata filters (for "theme" type) |

**Response:**
```json
{
  "status": "success",
  "estimate": {
    "total_documents": 50,
    "total_chunks": 50,
    "total_text_chars": 127845,
    "estimated_input_tokens": 31961,
    "estimated_output_tokens": 1000,
    "batch_count": 4,
    "cost_breakdown": {
      "input_cost": 0.96,
      "output_cost": 0.02,
      "total_cost": 0.98
    },
    "total_cost": 0.98,
    "cost_per_document": 0.02
  },
  "budget": {
    "can_proceed": true,
    "current_spending": 12.74,
    "monthly_cap": 20.0,
    "remaining_budget": 7.26,
    "would_exceed_by": 0.0
  },
  "analysis_type": "recent"
}
```

**Budget Check - Cannot Afford:**
```json
{
  "budget": {
    "can_proceed": false,
    "current_spending": 19.50,
    "monthly_cap": 20.0,
    "remaining_budget": 0.50,
    "would_exceed_by": 1.23
  }
}
```

**Analysis Types:**

**Recent (Last N Documents):**
```json
{
  "analysis_type": "recent",
  "limit": 50
}
```

**Full Database:**
```json
{
  "analysis_type": "full"
}
```

**Theme-Based (With Filters):**
```json
{
  "analysis_type": "theme",
  "filters": {
    "tradition": "vedic",
    "all_chakras": {"$in": ["heart", "crown"]}
  }
}
```

**Example:**
```bash
curl -X POST http://146.190.169.226:8000/estimate-analysis-cost \
  -H "Content-Type: application/json" \
  -d '{
    "analysis_type": "recent",
    "limit": 100
  }'
```

**Use Case:**
- Preview cost before running expensive analysis
- Check if you have budget remaining
- Plan multi-step analysis workflows

---

## Data Models

### UploadRequest

```typescript
{
  text: string;              // Document content (required)
  title: string;             // Document title (required)
  source?: string;           // Source identifier (optional)
  use_ai_tagging?: boolean;  // Enable AI tagging (default: false)
  ai_provider?: string;      // "ollama" or "openai" (default: "ollama")
  ollama_model?: string;     // Ollama model (default: "llama3.1")
}
```

### QueryRequest

```typescript
{
  question: string;                 // User's question (required)
  program_level?: string;           // "beginner"|"intermediate"|"advanced"
  filters?: Record<string, any>;    // Metadata filters
  top_k?: number;                   // Number of results (default: 5)
}
```

### QueryResponse

```typescript
{
  answer: string;              // Generated answer
  sources: Array<{
    title: string;             // Document title
    source: string;            // Source path
    score: number;             // Similarity score (0-1)
    tags: string[];            // Document tags
  }>;
  metadata: {
    matches_found: number;     // Number of matches
    program_level: string;     // Level used
    model: string;             // Claude model
  };
}
```

---

## Examples

### Complete Upload Workflow

```python
import requests

API_URL = "http://146.190.169.226:8000"

# 1. Check if document exists
check_response = requests.post(f"{API_URL}/check-duplicate", json={
    "title": "Heart Chakra Healing"
})

if check_response.json()["exists"]:
    print("Document already exists!")
    # Optionally delete and re-upload
    delete_response = requests.delete(f"{API_URL}/delete-document/Heart%20Chakra%20Healing")
    print(f"Deleted: {delete_response.json()}")

# 2. Upload document
with open("heart_chakra.md", "r") as f:
    content = f.read()

upload_response = requests.post(f"{API_URL}/upload", json={
    "text": content,
    "title": "Heart Chakra Healing",
    "source": "content/intermediate/heart_chakra.md",
    "use_ai_tagging": True,
    "ai_provider": "ollama"
})

print(upload_response.json())
# Output: {"status": "success", "chunks_created": 23, ...}

# 3. Verify upload
docs_response = requests.get(f"{API_URL}/uploaded-documents")
docs = docs_response.json()["documents"]
print(f"Total documents: {len(docs)}")
```

### Query with Advanced Filtering

```python
import requests

API_URL = "http://146.190.169.226:8000"

# Query for content about photon consciousness AND chakras
response = requests.post(f"{API_URL}/query", json={
    "question": "How does light relate to consciousness and energy centers?",
    "program_level": "advanced",
    "filters": {
        "bridge_concept": "photon_consciousness",
        "all_chakras": {"$in": ["crown", "third_eye"]}
    },
    "top_k": 10
})

result = response.json()
print(result["answer"])
print(f"\nSources used: {len(result['sources'])}")

for source in result["sources"]:
    print(f"- {source['title']} (score: {source['score']:.2f})")
```

### Cost Management

```python
import requests

API_URL = "http://146.190.169.226:8000"

# 1. Check current spending
dashboard = requests.get(f"{API_URL}/spending-dashboard").json()
print(f"Spent: ${dashboard['stats']['total_cost']}")
print(f"Remaining: ${dashboard['stats']['remaining_budget']}")

# 2. Estimate cost of analysis
estimate = requests.post(f"{API_URL}/estimate-analysis-cost", json={
    "analysis_type": "recent",
    "limit": 100
}).json()

print(f"Analysis would cost: ${estimate['estimate']['total_cost']}")

if estimate["budget"]["can_proceed"]:
    print("✓ Budget available - proceeding with analysis")
    # Run your analysis here
else:
    print(f"✗ Would exceed budget by ${estimate['budget']['would_exceed_by']}")

    # Increase cap if needed
    new_cap = requests.post(f"{API_URL}/update-spending-cap", json={
        "new_cap": 40.00
    }).json()
    print(f"Updated cap to ${new_cap['new_cap']}")
```

### Batch Document Upload

```python
import requests
from pathlib import Path

API_URL = "http://146.190.169.226:8000"

content_dir = Path("/content/beginner")
uploaded = 0
failed = 0

for file_path in content_dir.glob("*.md"):
    try:
        with open(file_path, "r") as f:
            content = f.read()

        response = requests.post(f"{API_URL}/upload", json={
            "text": content,
            "title": file_path.stem,
            "source": str(file_path),
            "use_ai_tagging": False  # Faster for bulk uploads
        }, timeout=120)

        if response.status_code == 200:
            print(f"✓ {file_path.name}")
            uploaded += 1
        else:
            print(f"✗ {file_path.name}: {response.text}")
            failed += 1

    except Exception as e:
        print(f"✗ {file_path.name}: {e}")
        failed += 1

print(f"\nResults: {uploaded} uploaded, {failed} failed")
```

---

## API Client Libraries

### Python

```python
class EvolveAPI:
    def __init__(self, base_url="http://146.190.169.226:8000"):
        self.base_url = base_url

    def upload(self, text, title, **kwargs):
        return requests.post(f"{self.base_url}/upload", json={
            "text": text,
            "title": title,
            **kwargs
        }).json()

    def query(self, question, **kwargs):
        return requests.post(f"{self.base_url}/query", json={
            "question": question,
            **kwargs
        }).json()

    def get_documents(self):
        return requests.get(f"{self.base_url}/uploaded-documents").json()

    def delete_document(self, title):
        import urllib.parse
        encoded = urllib.parse.quote(title)
        return requests.delete(f"{self.base_url}/delete-document/{encoded}").json()

# Usage
api = EvolveAPI()
api.upload(text="...", title="My Document")
result = api.query(question="What is consciousness?")
print(result["answer"])
```

### JavaScript/Node.js

```javascript
class EvolveAPI {
  constructor(baseUrl = "http://146.190.169.226:8000") {
    this.baseUrl = baseUrl;
  }

  async upload(text, title, options = {}) {
    const response = await fetch(`${this.baseUrl}/upload`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, title, ...options })
    });
    return response.json();
  }

  async query(question, options = {}) {
    const response = await fetch(`${this.baseUrl}/query`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question, ...options })
    });
    return response.json();
  }

  async getDocuments() {
    const response = await fetch(`${this.baseUrl}/uploaded-documents`);
    return response.json();
  }
}

// Usage
const api = new EvolveAPI();
const result = await api.query("What is consciousness?", {
  program_level: "beginner"
});
console.log(result.answer);
```

---

## Troubleshooting

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for detailed debugging guides.

**Quick Checks:**

1. **Server not responding:**
   ```bash
   ssh root@146.190.169.226 'systemctl status main'
   ```

2. **Upload failing:**
   - Check text length (empty text = error)
   - Verify timeout (120s default)
   - Test with smaller document first

3. **Query returns no results:**
   - Verify documents are uploaded: `GET /stats`
   - Try broader query or remove filters
   - Check program_level matches uploaded content

4. **Spending dashboard shows 0:**
   - Only tracks Claude analyses (not queries or uploads)
   - Use `/estimate-analysis-cost` to preview costs

---

## Support

**Documentation:**
- [Metadata Schema](METADATA_SCHEMA.md) - Complete field reference
- [Troubleshooting](TROUBLESHOOTING.md) - Common issues and solutions
- [Deployment Guide](DEPLOYMENT_GUIDE.md) - Server setup and configuration

**Server Info:**
- IP: 146.190.169.226
- Port: 8000
- Provider: DigitalOcean
- Region: US East

**Quick Test:**
```bash
curl http://146.190.169.226:8000/health
```

---

**Last Updated:** November 30, 2025
**API Version:** 1.0.0
