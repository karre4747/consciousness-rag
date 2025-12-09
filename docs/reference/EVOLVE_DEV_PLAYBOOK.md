# Evolve Dev Playbook

## Purpose
Capture the working plan that guided the recent sprint—the async Pinecone rework, OpenAI tagging hardening, documentation refresh, and housekeeping—so the next agent (or human) can see what was researched, why key decisions landed where they did, and where to take it next.

## Summary of Actions
- **Backend stability:** Wrapped every Pinecone call in `asyncio.to_thread()` with `asyncio.wait_for` and centralized retries in `pinecone_with_retry`. Health/stats endpoints now operate asynchronously against the hosted index endpoint and only expose serializable metrics.
- **Tagging resilience:** Promoted OpenAI tagging to `async` with retries/exponential backoff/timeouts, still falling back to keyword tagging on failure while using the shared client.
- **Documentation stack:** Authored a suite of new reference guides (`BACKEND_BEST_PRACTICES`, `PINECONE_BEST_PRACTICES`, `CSP_BEST_PRACTICES`, `FRONTEND_GUIDE`, `AGENT_OPERATIONS`, `EVOLVE_ENGINEERING_GUIDE`, etc.) that codify async patterns, retry logic, cost-awareness, CSP-safe UI patterns, and agent workflows.
- **Housekeeping & archiving:** Cleaned up legacy files (`expanded-tagging-v2.py`, the stubbed `api/`, `backend/ingest_content_UPDATED.py`, Pinecone/Claude/Ollama notes) by moving them under `archive/` so the root tree reflects only active assets.
- **Research artefact:** This playbook doubles as the plan-of-record, summarizing the context that produced the above work and providing a living reference for future Grok Developers.

## Key Concepts to Preserve
1. **Async boundary discipline:** Never call synchronous SDK methods directly; always wrap them in `asyncio.to_thread` + timeout + retry before touching Pinecone/OpenAI from FastAPI.
2. **Cost-conscious tagging:** Use GPT-3.5/Claude judiciously via retries and fallbacks; track Claude spend through `backend/spending_tracker.py`.
3. **CSP hygiene:** Avoid `unsafe-eval` and inline scripts; rely on documented CSP recommendations in `docs/reference/CSP_BEST_PRACTICES.md`.
4. **Agent specialization:** The doc-driven agent system now has explicit roles (backend, frontend, RAG, docs) outlined in `AGENT_OPERATIONS.md`; future agents should read that before acting.

## Immediate Next Steps
- Keep watching Pinecone response health using the improved `/health` and `/stats` endpoints; surface additional metrics if needed.
- Harden frontend assets against CSP warnings by following `FRONTEND_GUIDE` and phasing out inline scripts.
- Ensure Claude spending remains visible in `backend/claude_spending.db`, and update `CLAUDE_SPENDING_IMPLEMENTATION_STATUS` (archived) only if new insights emerge.
- Consider moving this playbook into `archive/` once it stabilizes, but keep the active copy in `docs/reference/` while the project is evolving.

## How to Use This Playbook
1. **New agent onboarding:** Read this file plus `EVOLVE_ENGINEERING_GUIDE.md` on day one to understand architecture, risks, and doc alignment requirements.
2. **For Claude Desktop/AI coding assistants:** Read `CLAUDE_CODING_GUIDE.md` for explicit step-by-step instructions on working with this codebase.
3. **Operational decisions:** Match every Pinecone/OpenAI change against the async/retry best practices in `BACKEND_BEST_PRACTICES.md` and `PINECONE_BEST_PRACTICES.md`.
4. **Documenting future work:** When adding references, update `DOC_ALIGNMENT_NOTES.md` so the knowledge graph stays in sync.

This playbook is your single source of truth for what just happened, why, and what to build next. Keep it in the reference docs for easy lookup, and move to `archive/` only when you believe the work has stabilized and no longer needs frequent updates.

