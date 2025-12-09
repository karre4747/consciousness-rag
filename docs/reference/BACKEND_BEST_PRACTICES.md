# Backend Best Practices

_Last updated: December 2025_

This guide distills the backend patterns already in use and how to extend them safely. It complements `EVOLVE_ENGINEERING_GUIDE.md`, `PINECONE_BEST_PRACTICES.md`, `CSP_BEST_PRACTICES.md`, `API_REFERENCE.md`, and `TESTING_GUIDE.md`.

## 1) Core principles
- **Async-first:** Treat FastAPI endpoints as non-blocking; offload blocking SDK calls with `asyncio.to_thread` or use native async clients where available.
- **Centralized retries/timeouts:** Wrap all external calls (Pinecone now; OpenAI/Claude if expanded) with shared helpers that enforce timeouts, classify errors, and apply backoff with jitter.
- **API-first boundaries:** Keep `backend/main.py` orchestration-focused; move reusable logic into helper modules.
- **Cost-aware defaults:** Use keyword/Ollama tagging by default; reserve OpenAI/Claude for high-value paths and gated workflows (cost estimator + spending tracker).
- **Safety & auth:** Plan for API keys/JWT and scoped CORS in production; add rate limiting for public exposure.

## 2) Lifespan and client reuse
- Initialize Pinecone/OpenAI/Anthropic once in the FastAPI lifespan; store singletons (`pinecone_client`, `openai_client`, `anthropic_client`, `index`).
- Use host-based Pinecone connection:
  ```python
  index_desc = pinecone_client.describe_index(PINECONE_INDEX_NAME)
  index = pinecone_client.Index(host=index_desc.host)
  ```
- Never create per-request clients; reuse shared instances.

## 3) Retry/timeout patterns
- **Pinecone:** Use `pinecone_with_retry` (async, to_thread, timeout, backoff + jitter). Retry only transient errors (5xx, 429, timeouts); do not retry 4xx (except 429).
- **OpenAI/Claude:** Mirror the same structure if adding retries—classify errors, cap retries, and timebox calls.
- **Timeout guidance:** Health 5s; query 10s; upsert 15–30s; large queries/analysis 30s. Surface HTTP 504 for timeouts.

## 4) Ingestion & metadata
- Keep chunking, tagging, and embedding idempotent and batch-friendly.
- Preserve structured IDs and metadata shape per `METADATA_SCHEMA.md` (no nested objects; strings/numbers/booleans/list-of-strings).
- Maintain both primary fields (e.g., `primary_chakra`) and comprehensive lists (`all_chakras`, `all_traditions`, etc.).

## 5) Cost controls
- Default tagging path: keyword → Ollama optional → OpenAI only when explicitly requested.
- Use `cost_estimator.py` + `spending_tracker.py` to check budget before Claude analysis; block or warn when over cap.
- Keep `top_k` modest and use metadata filters to narrow search space.

## 6) Error handling & responses
- Use `HTTPException` with clear messages for client-facing errors.
- Log retries and unexpected exceptions with context (endpoint, operation type).
- Avoid leaking secrets in error messages.

## 7) Security posture
- Add auth (API key/JWT) and app-level rate limiting before opening the API broadly.
- Tighten CORS for production (avoid `*`).
- Prepare to harden CSP once frontend scripts are externalized (`CSP_BEST_PRACTICES.md`).

## 8) Testing & validation
- Run `test_api.py` plus manual smoke tests from `TESTING_GUIDE.md` after backend changes:
  - `/health`, `/stats`
  - `/upload` (small + multi-chunk)
  - `/query` (basic + filtered)
  - Spending endpoints if touched
- For Pinecone changes, verify vector counts and metadata integrity via `/stats` and sample queries.

## 9) Observability (next steps)
- Adopt structured logging (JSON) and correlation IDs for long-running or multi-step operations (upload/analysis).
- Track basic metrics: request latency, retry counts, timeout counts, and error rates.

## 10) Change discipline
- Keep PRs/changes small and scoped (one concern at a time).
- Update or annotate relevant docs when behavior changes.
- Avoid schema drift: if tagging/metadata changes, update `METADATA_SCHEMA.md` and any consuming code.

