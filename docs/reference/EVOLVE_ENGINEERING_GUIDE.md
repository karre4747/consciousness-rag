# Evolve Engineering Guide

_Last updated: December 2025_

This guide captures the current architecture, risks, and design principles for the Evolve Consciousness Engine. It complements, not replaces, the existing reference docs (`ARCHITECTURE.md`, `API_REFERENCE.md`, `METADATA_SCHEMA.md`, `PINECONE_BEST_PRACTICES.md`, `CSP_BEST_PRACTICES.md`, `TESTING_GUIDE.md`, `TROUBLESHOOTING.md`).

## 1) Architecture at a glance
- **Backend:** FastAPI (`backend/main.py`), async-first, runs as `evolve.service` on DigitalOcean.
- **Core integrations:** Pinecone (vector store), OpenAI (embeddings + tagging), Anthropic Claude (RAG answers), optional Ollama tagging.
- **Tagging:** Hybrid keyword + AI (`backend/tagging.py`) aligned to the schema in `METADATA_SCHEMA.md`.
- **Docs/UI:** Single-page portal at `backend/static/index.html` for upload, tagging management, query, analysis, and spending dashboard.
- **Ops:** Systemd + optional nginx reverse proxy. Health, stats, and spending endpoints are live.

## 2) Current strengths
- **Async + retries:** Pinecone calls wrapped with `pinecone_with_retry`, timeouts per endpoint, host-based index connection (see `PINECONE_OPTIMIZATION_SUMMARY.md`).
- **Rich metadata:** Comprehensive tagging fields, primary and “all_*” lists; consistent with Pinecone constraints.
- **Cost controls:** Spending tracker and cost estimator exist; Claude budget cap logic is ready to be enforced in analysis flows.
- **Documentation depth:** Deployment, installation, architecture, testing, CSP, Pinecone best practices already documented.

## 3) Known gaps and risks
- **Auth & rate limiting:** API is open today; add API keys/JWT and app-level rate limits for production use.
- **CSP looseness:** Current headers allow `'unsafe-inline' 'unsafe-eval'`; tighten per `CSP_BEST_PRACTICES.md` once JS is externalized.
- **Observability:** Logging is basic; add structured logs and minimal metrics (latency, retries, failures).
- **MCP server:** Claude Desktop MCP is documented, but server code is not yet in-repo.
- **Doc drift:** Older docs (e.g., references to `expanded-tagging-v2.py`) should be kept in sync with `backend/tagging.py`.

## 4) Design principles
- **API-first:** Keep `backend/main.py` orchestration-focused; move heavy logic into helpers/modules.
- **Async safety:** All external I/O uses non-blocking patterns (`asyncio.to_thread` or native async). Centralize retry/timeout logic.
- **Cost-aware defaults:** Prefer keyword/Ollama tagging; reserve OpenAI/Claude for high-value paths. Use estimator + spending tracker for batch/analysis jobs.
- **Security posture:** Move toward auth, scoped CORS, stricter CSP, and basic rate limiting before broad exposure.
- **Testability:** Favor small, deterministic helpers; cover critical flows with `test_api.py` and manual scenarios from `TESTING_GUIDE.md`.

## 5) Backend expectations (summary)
- Reuse singletons for Pinecone/OpenAI/Anthropic; never create per-request clients.
- Use host-based Pinecone index; keep `pinecone_with_retry` for every Pinecone call; mirror similar pattern for OpenAI if expanded.
- Enforce timeouts on all external calls; set per-endpoint budgets (health 5s, query 10s, upsert 15–30s, long analysis 30s).
- Keep ingestion and tagging paths idempotent and chunk-friendly; preserve structured IDs and metadata shape in `METADATA_SCHEMA.md`.

## 6) Frontend expectations (summary)
- Short term: keep vanilla JS but extract inline scripts to external files, modularize functions, remove inline handlers/eval.
- Medium term: tighten CSP (drop `'unsafe-eval'`, then `'unsafe-inline'`), align with patterns in `CSP_BEST_PRACTICES.md`.
- UX: clear loading/error states for upload, query, analysis, and spending; responsive layout; basic accessibility (focus, aria for modals).
- Future: if complexity grows, migrate to a lightweight framework (React/Svelte) using the same API contracts.

## 7) Cost optimization playbook
- **Tagging:** keyword default → Ollama optional → OpenAI only for flagship content.
- **RAG:** keep `top_k` modest; use metadata filters to narrow search; avoid over-fetching.
- **Analysis:** always estimate cost first; enforce spending caps; batch thoughtfully.
- **Infra:** keep droplet lean; use host-based Pinecone to avoid extra calls; consider gRPC extras only if throughput needs rise.

## 8) Operations checklist (high level)
- Health: `/health`, `/api`, `/stats`.
- Content: `/upload`, `/uploaded-documents`, `/delete-document/{title}`, `/verify-tagging`, `/retag-documents`.
- Spending: `/spending-dashboard`, `/update-spending-cap`, `/estimate-analysis-cost`.
- Logs: `journalctl -u evolve -f`; service control via `systemctl`.

## 9) References
- Architecture: `docs/reference/ARCHITECTURE.md`
- API: `docs/reference/API_REFERENCE.md`
- Metadata: `docs/reference/METADATA_SCHEMA.md`
- Pinecone: `docs/reference/PINECONE_BEST_PRACTICES.md`
- CSP: `docs/reference/CSP_BEST_PRACTICES.md`
- Testing/Troubleshooting: `docs/reference/TESTING_GUIDE.md`, `docs/reference/TROUBLESHOOTING.md`


