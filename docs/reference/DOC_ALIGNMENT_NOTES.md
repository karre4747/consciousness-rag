# Doc Alignment Notes

_Last updated: December 2025_

Quick record of cross-checks performed to keep documentation consistent with the current implementation and new guidance files.

## Reviewed and aligned
- `PHASE_1_COMPLETE.md` — Still accurate for backend feature set and deployment status.
- `EVOLVE_HANDOFF_DOCUMENT.md` — Matches current architecture and tagging approach; references to `expanded-tagging-v2.py` remain historically informative but the live code is `backend/tagging.py`.
- `archive/PROJECT_SUMMARY.md` — High-level vision and two-tier AI strategy remain valid; no action needed.
- `docs/reference/ARCHITECTURE.md` — Consistent with current backend, Pinecone host-based connection, and portal UI endpoints.
- `docs/reference/API_REFERENCE.md` — Endpoint descriptions match the current FastAPI app, including upload/query/stats/spending routes.
- `docs/reference/PINECONE_BEST_PRACTICES.md` — Aligns with the implemented optimizations (host-based index, async wrappers, timeouts/retries).
- `docs/reference/CSP_BEST_PRACTICES.md` — Guidance stands; current CSP is looser and will be tightened after frontend refactor (see `FRONTEND_GUIDE.md`).

## Notes / minor clarifications
- Tagging implementation is unified in `backend/tagging.py`; older mentions of `expanded-tagging-v2.py` are legacy context only.
- CSP hardening is planned post-frontend refactor to external JS (see `FRONTEND_GUIDE.md`).
- MCP server is documented (`CLAUDE_DESKTOP_SETUP.md`) but not yet implemented in-repo.

## Future alignment triggers
- When tightening CSP, update `API_REFERENCE.md` and `ARCHITECTURE.md` with the new header policy.
- If auth/rate-limiting is added, update `API_REFERENCE.md`, `DEPLOYMENT_CHECKLIST.md`, and `EVOLVE_ENGINEERING_GUIDE.md`.
- If tagging schema changes, update `METADATA_SCHEMA.md`, `EVOLVE_TAGGING_AND_CONNECTIONS.md`, and `API_REFERENCE.md` examples.


