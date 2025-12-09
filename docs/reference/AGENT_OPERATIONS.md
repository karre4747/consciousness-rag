# Agent Operations Guide

_Last updated: December 2025_

This guide defines the roles, responsibilities, and working agreements for future human or AI agents collaborating on the Evolve Consciousness Engine. It is designed to reduce ambiguity, prevent regressions, and keep work aligned with existing documentation and code.

## 1) Roles

### Backend & Infra Agent
- **Owns:** `backend/main.py`, `backend/tagging.py`, `backend/spending_tracker.py`, `backend/cost_estimator.py`, `evolve.service`, `nginx.conf`.
- **Focus:** API correctness, async safety, retries/timeouts, cost awareness, auth/rate limiting, observability.
- **Key references:** `ARCHITECTURE.md`, `API_REFERENCE.md`, `PINECONE_BEST_PRACTICES.md`, `EVOLVE_ENGINEERING_GUIDE.md`.

### Frontend & UX Agent
- **Owns:** `backend/static/index.html` and future assets under `backend/static/js/`, `backend/static/css/`.
- **Focus:** Modular JS (no inline eval), responsive UI, accessibility, CSP compliance, clear UX states.
- **Key references:** `FRONTEND_GUIDE.md`, `CSP_BEST_PRACTICES.md`, `TESTING_GUIDE.md` (UI flows).

### RAG & Knowledge Modeling Agent
- **Owns:** Tagging logic (`backend/tagging.py`), metadata schema (`METADATA_SCHEMA.md`), query/prompt behaviors in `backend/main.py`.
- **Focus:** Tag/schema evolution, relevance tuning, filter design, prompt quality, explainability.
- **Key references:** `METADATA_SCHEMA.md`, `EVOLVE_TAGGING_AND_CONNECTIONS.md`, `API_REFERENCE.md`.

### Docs & Orchestration Agent
- **Owns:** Cross-cutting docs and playbooks (e.g., this file, `EVOLVE_ENGINEERING_GUIDE.md`, `FRONTEND_GUIDE.md`, `BACKEND_BEST_PRACTICES.md`).
- **Focus:** Keep docs synced with code, outline workflows, highlight pitfalls, and maintain checklists.
- **Key references:** All reference docs; ensures consistency.

## 2) Operating rhythm

- **Read before change:** For any target area, skim the relevant reference docs first.
- **Small, reviewable changes:** Prefer focused, well-scoped edits; avoid mixing concerns.
- **Tests/checks:** Run relevant smoke tests (API calls, UI flows) after changes; follow `TESTING_GUIDE.md`.
- **Cost & safety:** Default to cost-aware paths (keyword/Ollama) and non-blocking I/O; avoid widening CSP until vetted.
- **Auth posture:** Assume future production needs auth/rate limiting; do not add public features without considering this.

## 3) Change boundaries & patterns

- **Backend:**
  - Keep `main.py` orchestration-focused; factor reusable logic into helpers.
  - All external I/O must have timeouts and, when applicable, retries (see `pinecone_with_retry` pattern).
  - Maintain structured metadata per `METADATA_SCHEMA.md`; avoid schema drift.

- **Frontend:**
  - Move inline JS into external modules; avoid `eval`, string-based timers, and inline handlers.
  - Keep CSP in mind—design for a `'self'` + external-script model without `'unsafe-eval'`.
  - Preserve UX clarity: loading, error, success states for upload/query/tagging/analysis/spending.

- **Docs:**
  - Update or annotate docs when behaviors change; avoid stale references (e.g., old model names or scripts).
  - Cross-link to authoritative docs instead of duplicating long sections.

## 4) Pitfalls to avoid

- Blocking the event loop with synchronous SDK calls.
- Introducing CSP regressions via inline scripts or `unsafe-eval`.
- Schema drift between `tagging.py` and `METADATA_SCHEMA.md`.
- Shipping unauthenticated public endpoints without rate limiting.
- Large, mixed-purpose commits/PRs that are hard to review.

## 5) Definition of done (per change)

- Relevant docs referenced and updated (or noted as N/A).
- Timeouts/retries considered for any new external I/O.
- Cost impact considered (OpenAI/Claude/Pinecone usage).
- Tests or manual checks run appropriate to the change scope.
- No new CSP or security regressions; no stale references introduced.

## 6) Quick-start checklists

- **Backend change:** Read `EVOLVE_ENGINEERING_GUIDE.md` → align with async/retry/cost patterns → run API smoke tests → note doc impact.
- **Frontend change:** Read `FRONTEND_GUIDE.md` → avoid inline/eval → ensure UI states and accessibility → test key flows in the browser.
- **Tagging/schema change:** Read `METADATA_SCHEMA.md` → update tagging logic and docs together → validate Pinecone constraints.
- **Docs change:** Keep concise; link to sources; ensure consistency with current code and configs.

