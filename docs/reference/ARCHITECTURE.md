# Evolve Consciousness RAG - System Architecture

**Last Updated:** November 30, 2025
**Version:** 1.0.0

---

## 🎯 System Overview

The Evolve Consciousness RAG system is a comprehensive knowledge base for addiction recovery and spiritual ascension content, designed to support course creation and research.

### **Purpose:**
- Enable deep research across consciousness, mysticism, and recovery literature
- Power the evolveAI MCP server for Claude Desktop integration
- Support creation of 90-day addiction recovery program content
- Map 12-step recovery to mystical ascension processes

---

## 🏗️ Architecture Components

### **1. Pinecone Vector Database**
- **Purpose:** Store and search consciousness content semantically
- **Index:** `evolve-consciousness`
- **Dimension:** 1536 (OpenAI text-embedding-3-large)
- **Metric:** Cosine similarity
- **Cloud:** AWS us-east-1

### **2. DigitalOcean Backend (FastAPI)**
- **Server:** 146.190.169.226:8000
- **Framework:** FastAPI + Uvicorn
- **Endpoints:**
  - `POST /upload` - Upload documents with AI tagging
  - `POST /query` - RAG query with Claude Sonnet 4.5
  - `GET /uploaded-documents` - List all documents
  - `POST /check-duplicate` - Check for duplicate uploads
  - `DELETE /delete-document/{title}` - Remove documents
  - `GET /spending-dashboard` - Claude API spending tracker
  - `POST /estimate-analysis-cost` - Cost estimation

### **3. evolveAI MCP Server (To Be Built)**
- **Purpose:** Connect Claude Desktop to Pinecone database
- **Protocol:** Model Context Protocol (MCP)
- **Location:** Local Mac installation
- **Tool:** `query_consciousness_library`

### **4. Frontend Upload Interface**
- **URL:** http://localhost:8000 (via SSH tunnel)
- **Features:**
  - Drag & drop document upload
  - Duplicate detection
  - Document management (search, delete)
  - Progress tracking
  - AI tagging options (Ollama/OpenAI)

---

## 📊 Data Flow

### **Upload Flow:**
```
User uploads PDF/TXT/DOCX
    ↓
Frontend reads file as UTF-8
    ↓
Clean problematic characters
    ↓
Backend chunks text (1000 tokens, 200 overlap)
    ↓
Process in batches of 50 chunks:
    ├─ Generate OpenAI embedding (1536 dims)
    ├─ Generate tags (keyword/Ollama/OpenAI)
    └─ Clean all text to ASCII
    ↓
Upsert to Pinecone with metadata
```

### **Query Flow:**
```
User asks question (via MCP or UI)
    ↓
Convert question to OpenAI embedding
    ↓
Pinecone semantic search (top 5 chunks)
    ↓
Retrieved chunks + question → Claude Sonnet 4.5
    ↓
Claude generates comprehensive answer
    ↓
Return answer + source citations with metadata
```

---

## 🗄️ Metadata Schema

### **Core Fields:**
- `text` (string) - Chunk content (ASCII-safe)
- `title` (string) - Document title
- `source` (string) - Original filename
- `chunk_index` (number) - Chunk position
- `total_chunks` (number) - Total chunks in document

### **Tagging Fields:**
- `tags` (list[string]) - General tags (max 50)
- `primary_theme` (string) - Main theme
- `consciousness_level` (string) - Hawkins scale level
- `emotions` (list[string]) - Detected emotions

### **Primary Fields (Individual):**
- `primary_chakra` (string) - First/main chakra mentioned
- `tradition` (string) - Primary spiritual tradition
- `teacher` (string) - Primary teacher/author
- `ascension_path` (string) - Main ascension process
- `bridge_concept` (string) - Main bridge concept
- `recovery_focus` (string) - Addiction type
- `healing_modality` (string) - Primary healing approach

### **Comprehensive Fields (All detected - Lists):**
- `all_chakras` (list[string]) - ALL chakras mentioned
- `all_meridians` (list[string]) - ALL meridians
- `all_12_steps` (list[string]) - ALL 12-step references
- `all_consciousness_levels` (list[string]) - ALL levels mentioned
- `all_traditions` (list[string]) - ALL traditions referenced
- `all_teachers` (list[string]) - ALL teachers/authors
- `all_quantum_physics` (list[string]) - Quantum concepts
- `all_quantum_particles` (list[string]) - Particle types
- `all_ascension_paths` (list[string]) - ALL ascension processes
- `all_bridge_concepts` (list[string]) - ALL bridge concepts
- `all_universal_laws` (list[string]) - Universal laws
- `all_healing_modalities` (list[string]) - ALL healing modalities
- `all_sacred_geometry` (list[string]) - Sacred geometry
- `all_subtle_bodies` (list[string]) - Subtle body references
- `all_addiction_types` (list[string]) - Addiction types

### **Optional Fields:**
- `program_level` (string) - For addiction content (beginner/intermediate/advanced)

---

## 🔧 Technology Stack

### **Backend:**
- Python 3.10+
- FastAPI (web framework)
- Uvicorn (ASGI server)
- Pinecone SDK 8.0.0
- OpenAI SDK (embeddings + GPT)
- Anthropic SDK (Claude Sonnet 4.5)
- tiktoken (token counting)

### **Frontend:**
- HTML5 + CSS3
- Vanilla JavaScript
- Fetch API for backend calls

### **Infrastructure:**
- DigitalOcean droplet
- SSH tunnel for local access
- Git version control (GitHub)

### **AI Services:**
- OpenAI text-embedding-3-large (embeddings)
- Claude Sonnet 4.5 (RAG analysis)
- Ollama llama3.1 (optional tagging - local)
- OpenAI GPT-3.5 (optional tagging - cloud)

---

## 💰 Cost Management

### **Spending Tracker:**
- SQLite database (`claude_spending.db`)
- Monthly cap: $20 for Claude API
- Tables: `spending_history`, `monthly_caps`
- Pre-query cost estimation using tiktoken

### **Pricing:**
- Claude Sonnet 4.5: $3/1M input, $15/1M output tokens
- OpenAI embeddings: $0.13/1M tokens
- Ollama: FREE (local)
- OpenAI GPT-3.5 tagging: $0.40/1000 docs

---

## 🔐 Security & Data Handling

### **Character Encoding:**
- All text cleaned to ASCII before storage
- Unicode normalization (NFKC)
- Smart quotes → regular quotes
- Control characters removed
- Prevents Pinecone encoding errors

### **Duplicate Prevention:**
- Check metadata by title before upload
- Warning dialog with proceed/skip option
- Document list with search/delete capabilities

### **Error Handling:**
- Batch processing with per-chunk error recovery
- Detailed logging for debugging
- Graceful degradation on failures

---

## 🎯 Use Cases

### **For Course Creator (You):**
1. Upload consciousness/recovery books to Pinecone
2. Use evolveAI MCP in Claude Desktop for research
3. Ask: "How does Step 4 relate to Dark Night of the Soul?"
4. Get comprehensive answers citing multiple sources
5. Use research to create course content
6. Export to Notion → Deploy to student app

### **Query Examples:**
- "Map the 12 steps to chakra awakening progression"
- "Compare surrender in 12-steps vs mystical traditions"
- "What astrological correspondences exist for Step 1?"
- "How do Steiner and Blavatsky discuss the etheric body?"
- "Find all references to ego death across traditions"

---

## 🔄 Integration Points

### **Current:**
- Claude Desktop (via MCP) → evolveAI server → DigitalOcean API → Pinecone
- Browser UI → localhost:8000 → DigitalOcean API → Pinecone

### **Future (Student App):**
- Student Frontend → evolveAI.ts (Supabase Sage AI) - Fast, personalized
- Student Frontend → evolveAI.ts → DigitalOcean API → Pinecone - Deep research (premium)

### **Separation of Concerns:**
- **Supabase:** User data, progress, journal entries, authentication
- **Pinecone:** Consciousness library for research and deep queries
- **evolveAI.ts:** Routing logic between fast/deep AI systems

---

## 📈 Scalability

### **Current Capacity:**
- Handles entire books (100+ pages)
- Batch processing (50 chunks at a time)
- Tested with Thomas Troward book (~300 chunks)

### **Future Growth:**
- Can scale to 1000s of documents
- Pinecone handles millions of vectors
- Metadata supports rich filtering for membership tiers

---

## 🧪 Testing Strategy

### **Manual Testing:**
1. Upload test document
2. Verify chunking and metadata
3. Query for test concepts
4. Validate source citations
5. Check metadata accuracy

### **Integration Testing:**
- MCP server → DigitalOcean API
- Query UI → Backend endpoints
- Duplicate detection flow
- Document management features

---

## 📚 Documentation Structure

```
consciousness-rag/
├── ARCHITECTURE.md (this file)
├── PROJECT_SUMMARY.md (overview)
├── API_REFERENCE.md (endpoints)
├── METADATA_SCHEMA.md (field details)
├── INSTALLATION.md (setup guide)
├── CLAUDE_DESKTOP_SETUP.md (MCP config)
├── TROUBLESHOOTING.md (common issues)
└── .claude/
    ├── project-context.md (AI assistant context)
    └── decisions.md (design decisions)
```

---

## 🔮 Future Enhancements

### **Phase 2 (Post-Launch):**
- Add evolveAI MCP queries to student-facing app
- Route deep questions to Pinecone, simple to Supabase
- Premium tier access to comprehensive research
- Analytics on most-queried topics
- Personalized recommendations based on user progress

### **Potential Features:**
- Multi-language support
- Audio/video content processing
- Image recognition for sacred geometry
- Community-contributed content
- Course marketplace integration

---

**End of Architecture Document**
