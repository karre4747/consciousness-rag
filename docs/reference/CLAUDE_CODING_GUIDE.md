# Claude Coding Guide for Evolve Consciousness Engine

**Purpose:** This guide provides explicit instructions for Claude Desktop (via MCP) or any AI coding assistant working on the Evolve Consciousness Engine codebase. Follow these directions to maintain code quality, avoid regressions, and align with established patterns.

**Last Updated:** December 2025

---

## 🎯 Quick Start: Before You Begin

**MANDATORY READING (in order):**
1. Read `EVOLVE_DEV_PLAYBOOK.md` - Understand what's been done and why
2. Read `EVOLVE_ENGINEERING_GUIDE.md` - Architecture, risks, and design principles
3. Read `AGENT_OPERATIONS.md` - Your role and responsibilities
4. Read the relevant best practices guide for your task:
   - Backend work → `BACKEND_BEST_PRACTICES.md`
   - Frontend work → `FRONTEND_GUIDE.md` + `CSP_BEST_PRACTICES.md`
   - Tagging/RAG → `METADATA_SCHEMA.md` + `PINECONE_BEST_PRACTICES.md`

**Then proceed with your task.**

---

## 📋 Core Principles (Never Violate)

### 1. Async Boundary Discipline
**CRITICAL:** Never call synchronous SDK methods directly in FastAPI endpoints.

**✅ CORRECT:**
```python
async def some_endpoint():
    result = await pinecone_with_retry(
        lambda: index.query(vector=embedding, top_k=5)
    )
```

**❌ WRONG:**
```python
async def some_endpoint():
    result = index.query(vector=embedding, top_k=5)  # BLOCKS EVENT LOOP
```

**Reference:** `BACKEND_BEST_PRACTICES.md` and `PINECONE_BEST_PRACTICES.md`

### 2. Cost-Conscious Design
- Default to keyword-based tagging (free)
- Use Ollama for AI tagging when possible (free, local)
- Use OpenAI GPT-3.5-turbo ($0.50/1M tokens) before Claude ($15/1M tokens)
- Always track Claude spending via `backend/spending_tracker.py`
- Never call Claude without budget checks

**Reference:** `BACKEND_BEST_PRACTICES.md` (Cost-Aware Design section)

### 3. CSP Hygiene
- **Never** use `eval()`, `new Function()`, or string-based `setTimeout`/`setInterval`
- **Never** add inline event handlers (`onclick="..."`)
- **Never** add inline `<script>` tags (except with nonces if absolutely necessary)
- Externalize all JavaScript to `backend/static/js/` files
- Target CSP: `script-src 'self'` (no `unsafe-eval`, no `unsafe-inline`)

**Reference:** `FRONTEND_GUIDE.md` and `CSP_BEST_PRACTICES.md`

### 4. Retry & Timeout Patterns
All external I/O (Pinecone, OpenAI, Claude) must have:
- Timeouts (`asyncio.wait_for` with appropriate timeout)
- Retry logic with exponential backoff
- Proper error handling (don't retry on 4xx client errors)

**Reference:** `BACKEND_BEST_PRACTICES.md` (Retry Logic section)

---

## 🚀 Immediate Next Steps (Priority Order)

### Priority 1: Frontend CSP Hardening ⚠️ **HIGH PRIORITY**

**Status:** NOT STARTED - This is the most critical pending work.

**Task:** Follow `FRONTEND_GUIDE.md` Stage 1 & Stage 2

**Steps:**
1. **Externalize JavaScript:**
   - Move all inline `<script>` code from `backend/static/index.html` to `backend/static/js/app.js`
   - Split into modules: `Upload`, `Docs`, `Tagging`, `Analysis`, `Research`, `Spending`, `UIHelpers`
   - Load with `<script src="/static/js/app.js" defer></script>`

2. **Remove Inline Handlers:**
   - Replace all `onclick="..."` attributes with `addEventListener` calls
   - Current count: 18 inline handlers (found via grep)
   - Example locations: tab buttons, analysis buttons, document actions

3. **Tighten CSP:**
   - Update `backend/main.py` CSP headers
   - Remove `'unsafe-eval'` and `'unsafe-inline'` from `script-src`
   - Target: `script-src 'self'` (plus nonce if interim inline code remains temporarily)

4. **Verify:**
   - Test all UI flows: upload, tagging, analysis, documents, query
   - Check browser console for CSP violations
   - Ensure no functionality breaks

**Reference:** `FRONTEND_GUIDE.md` (Stages 1-2), `CSP_BEST_PRACTICES.md`

---

### Priority 2: Monitor & Optimize Backend Health

**Status:** Implemented, but keep monitoring

**Tasks:**
- Monitor `/health` and `/stats` endpoints for Pinecone response times
- Surface additional metrics if needed (e.g., average query latency, error rates)
- Consider adding Prometheus/OpenTelemetry if observability gaps emerge

**Reference:** `EVOLVE_DEV_PLAYBOOK.md` (Immediate Next Steps)

---

### Priority 3: Documentation Alignment

**Status:** Ongoing maintenance

**Tasks:**
- When making code changes, update `DOC_ALIGNMENT_NOTES.md` if behavior changes
- Ensure all `.md` files reference current implementation (not legacy code)
- Cross-link related docs instead of duplicating content

**Reference:** `DOC_ALIGNMENT_NOTES.md`

---

## 🔧 Working on Specific Areas

### Backend Changes (`backend/main.py`, `backend/tagging.py`)

**Before starting:**
1. Read `BACKEND_BEST_PRACTICES.md`
2. Read `PINECONE_BEST_PRACTICES.md`
3. Understand the `pinecone_with_retry` helper pattern

**During work:**
- Wrap all Pinecone calls with `pinecone_with_retry()`
- Wrap all OpenAI/Claude calls with async + retry + timeout
- Use `asyncio.to_thread()` for blocking SDK calls
- Set appropriate timeouts (30s for Pinecone, 15s for OpenAI)
- Track costs if using Claude

**After work:**
- Test endpoints: `/health`, `/stats`, `/upload`, `/query`
- Check logs for errors
- Verify no blocking calls introduced

**Reference:** `BACKEND_BEST_PRACTICES.md`, `PINECONE_BEST_PRACTICES.md`

---

### Frontend Changes (`backend/static/index.html`)

**Before starting:**
1. Read `FRONTEND_GUIDE.md` (all stages)
2. Read `CSP_BEST_PRACTICES.md`
3. Understand current CSP violations

**During work:**
- **NEVER** add inline scripts or handlers
- Use `addEventListener` for all event handling
- Externalize all JavaScript to `backend/static/js/`
- Escape HTML when injecting user content (`escapeHtml` helper)
- Maintain clear loading/error/success states

**After work:**
- Test in browser with DevTools open
- Check Console for CSP violations
- Test all tabs: Upload, Tagging, Analysis, Documents, Query
- Verify responsive layout (mobile/tablet/desktop)

**Reference:** `FRONTEND_GUIDE.md`, `CSP_BEST_PRACTICES.md`

---

### Tagging & Metadata Changes (`backend/tagging.py`)

**Before starting:**
1. Read `METADATA_SCHEMA.md`
2. Read `EVOLVE_TAGGING_AND_CONNECTIONS.md`
3. Understand the three-pass tagging system:
   - Pass 1: Keyword-based (free)
   - Pass 2: AI enhancement (Ollama/OpenAI)
   - Pass 3: Claude deep analysis (expensive, tracked)

**During work:**
- Maintain schema compatibility with `METADATA_SCHEMA.md`
- Keep keyword fallback for AI failures
- Use async patterns for AI calls
- Track Claude spending for Pass 3

**After work:**
- Test tagging with `/upload` endpoint
- Verify metadata structure matches schema
- Check Pinecone constraints (field names, types)

**Reference:** `METADATA_SCHEMA.md`, `BACKEND_BEST_PRACTICES.md`

---

## 🚫 Common Pitfalls (Avoid These)

### ❌ Blocking the Event Loop
```python
# WRONG - Blocks FastAPI event loop
result = index.query(vector=embedding, top_k=5)

# CORRECT - Non-blocking
result = await pinecone_with_retry(
    lambda: index.query(vector=embedding, top_k=5)
)
```

### ❌ CSP Violations
```html
<!-- WRONG - Inline handler -->
<button onclick="doSomething()">Click</button>

<!-- CORRECT - External handler -->
<button id="myBtn">Click</button>
<script src="/static/js/app.js"></script>
<!-- In app.js: document.getElementById('myBtn').addEventListener('click', doSomething) -->
```

### ❌ Schema Drift
```python
# WRONG - Adding field not in METADATA_SCHEMA.md
metadata = {
    "title": doc.title,
    "new_field": "value"  # Not documented!
}

# CORRECT - Update METADATA_SCHEMA.md first, then use
```

### ❌ Cost Ignorance
```python
# WRONG - Calling Claude without budget check
response = claude_client.messages.create(...)

# CORRECT - Check budget first
if spending_tracker.would_exceed_budget(estimated_cost):
    raise HTTPException(402, "Budget exceeded")
response = await claude_with_retry(...)
```

---

## 📚 Documentation Structure

When working on the codebase, reference these docs:

**Architecture & Design:**
- `EVOLVE_ENGINEERING_GUIDE.md` - High-level architecture, risks, design principles
- `ARCHITECTURE.md` - System architecture details
- `EVOLVE_DEV_PLAYBOOK.md` - Recent work summary and next steps

**Backend:**
- `BACKEND_BEST_PRACTICES.md` - FastAPI, async, retry, cost patterns
- `PINECONE_BEST_PRACTICES.md` - Pinecone integration patterns
- `API_REFERENCE.md` - Endpoint documentation

**Frontend:**
- `FRONTEND_GUIDE.md` - Staged refactor plan and standards
- `CSP_BEST_PRACTICES.md` - Content Security Policy guidance

**RAG & Tagging:**
- `METADATA_SCHEMA.md` - Vector metadata structure
- `EVOLVE_TAGGING_AND_CONNECTIONS.md` - Tagging system details

**Operations:**
- `AGENT_OPERATIONS.md` - Agent roles and workflows
- `TESTING_GUIDE.md` - Testing procedures
- `TROUBLESHOOTING.md` - Debugging guide
- `DEPLOYMENT_CHECKLIST.md` - Deployment steps

**Cross-cutting:**
- `DOC_ALIGNMENT_NOTES.md` - Documentation consistency notes

---

## ✅ Definition of Done Checklist

Before marking any task complete, verify:

- [ ] Relevant reference docs read and understood
- [ ] Code follows async patterns (no blocking calls)
- [ ] Retries/timeouts implemented for external I/O
- [ ] Cost impact considered (Claude/OpenAI/Pinecone)
- [ ] CSP compliance (no inline scripts/handlers if frontend work)
- [ ] Schema compatibility (if metadata changes)
- [ ] Tests or manual checks run
- [ ] Documentation updated (or noted as N/A)
- [ ] No new security regressions
- [ ] No stale references introduced

---

## 🎓 Example Workflows

### Example 1: Adding a New Backend Endpoint

1. **Read:** `BACKEND_BEST_PRACTICES.md`, `API_REFERENCE.md`
2. **Design:** Endpoint signature, async/await pattern, error handling
3. **Implement:**
   - Use `@app.post("/new-endpoint")` decorator
   - Wrap external calls with `pinecone_with_retry()` or similar
   - Add timeout and retry logic
   - Track costs if using Claude
4. **Test:** Call endpoint, verify response, check logs
5. **Document:** Update `API_REFERENCE.md` if needed

### Example 2: Refactoring Frontend JavaScript

1. **Read:** `FRONTEND_GUIDE.md` (Stages 1-2), `CSP_BEST_PRACTICES.md`
2. **Identify:** Inline scripts/handlers to externalize
3. **Implement:**
   - Create `backend/static/js/app.js` (or module file)
   - Move inline code to external file
   - Replace `onclick="..."` with `addEventListener`
   - Update HTML to load external script
4. **Test:** Browser DevTools, check CSP violations, test all flows
5. **Update CSP:** Remove `unsafe-inline`/`unsafe-eval` from `main.py`

### Example 3: Enhancing Tagging System

1. **Read:** `METADATA_SCHEMA.md`, `backend/tagging.py`, `EVOLVE_TAGGING_AND_CONNECTIONS.md`
2. **Design:** New tags/metadata fields (update schema doc first)
3. **Implement:**
   - Update `generate_tags_keyword_based()` or AI tagging functions
   - Maintain async patterns
   - Keep fallback to keyword tags
4. **Test:** Upload document, verify tags/metadata structure
5. **Document:** Update `METADATA_SCHEMA.md` and `DOC_ALIGNMENT_NOTES.md`

---

## 🔍 When You're Stuck

1. **Check the logs:**
   - Backend: Terminal where `python main.py` runs
   - Frontend: Browser DevTools Console
   - Claude Desktop: `~/Library/Logs/Claude/mcp.log` (macOS)

2. **Review relevant docs:**
   - Error related to Pinecone? → `PINECONE_BEST_PRACTICES.md`
   - CSP violation? → `CSP_BEST_PRACTICES.md`
   - Async/blocking issue? → `BACKEND_BEST_PRACTICES.md`

3. **Test manually:**
   - Use `curl` to test API endpoints
   - Use browser DevTools to inspect frontend
   - Check Pinecone console for index status

4. **Check alignment:**
   - Does code match `METADATA_SCHEMA.md`?
   - Does behavior match `API_REFERENCE.md`?
   - Are docs consistent with `DOC_ALIGNMENT_NOTES.md`?

---

## 📝 Notes for Future Agents

- **This codebase prioritizes:** Cost-effectiveness, security (CSP), async safety, and maintainability
- **Current state:** Backend is production-ready; frontend needs CSP hardening (Priority 1)
- **Architecture:** FastAPI backend, vanilla JS frontend (no framework), Pinecone vector DB, OpenAI/Claude/Ollama for AI
- **Cost model:** Free (keyword/Ollama) → Cheap (OpenAI) → Expensive (Claude) - always prefer cheaper options
- **Security posture:** CSP-compliant frontend (target), async-safe backend (achieved), cost-tracked AI usage (achieved)

---

## 🎯 Summary: Your Mission

When working on this codebase:

1. **Read first** - Always start with relevant reference docs
2. **Follow patterns** - Use established async/retry/CSP patterns
3. **Be cost-aware** - Default to free/cheap options, track expensive calls
4. **Test thoroughly** - Verify no regressions, check CSP, test flows
5. **Document changes** - Update docs or note why not needed

**Most Important:** The frontend CSP hardening (Priority 1) is the highest-impact pending work. When ready, follow `FRONTEND_GUIDE.md` Stages 1-2 explicitly.

---

**This guide is your roadmap. Follow it, and you'll maintain the high code quality standards established in the Evolve Consciousness Engine.**

