# Status & Next Actions

> Where the work actually stands. Update at the end of each session.
> Last updated: **August 16, 2026**

## Done this session

**Repo restructure.** The project was nested as
`~/consciousness-RAG/consciousness-rag/` — a folder inside a same-named folder.
The inner one was always the real project (git repo, all recent work). It is now
`~/Developer/consciousness-rag/`. Old locations moved to `~/Developer/Archive/`,
untouched.

**Backups** at `~/Developer/_backups/consciousness-rag_20260816/` — `.env`,
`consciousness.db`, full git bundle (verified restorable), Claude Desktop config.
Neither `.env` nor the DB is in git; these are the only copies.

**GitHub.** 4 commits of agent architecture existed only on this drive. `gh` CLI
installed, authenticated as `karre4747`, credential in keyring. All pushed;
`origin/agentic-version` is current.

**MCP server** moved into the repo; Claude Desktop config repointed to
`~/Developer/consciousness-rag/mcp-server/`. Both venvs rebuilt.

**Library inventory** (`tools/inventory.py`, `known_authors.py`, `dedupe.py`):
scanned 11,707 files drive-wide → 502 candidates → after dedup and separating
Karre's own work:

- **354 source documents** → `library/`
- **52 own content** → `my_content/`
- **99 duplicates** → skipped, preferring OCR versions

Authors resolved for 222, including shorthand no model could infer (BHBY →
Dispenza, POSM → Murphy, CT → Fleet).

**Chunking decided.** Compared the current fixed-window chunker against
Chonkie's `RecursiveChunker` on Fleet's *Rays of the Dawn*: 6 chunks cutting
mid-word vs. 21 respecting paragraph structure. **Chonkie RecursiveChunker
wins** — but the test also showed OCR text carries soft hyphens (`work­`,
`spirit­ual`), so **text cleaning must precede chunking** or broken words get
embedded.

**Framework mappings captured** — chakras ↔ 12 Steps ↔ Fleet's creation arc.
See `PROJECT_CONTEXT.md`.

## Next actions, in order

1. **Organize files** — copy the 354 into `library/`, 52 into `my_content/`.
   Copy, don't move; originals stay until proven.

2. **Build the ingestion pipeline.** This is the critical piece — Karre is about
   to add documents in volume, and it must be one reliable path before that
   starts:
   - extract text → **detect low yield → OCR or quarantine** (never silently
     ingest an image-only PDF as an empty record)
   - clean OCR artifacts (soft hyphens, line breaks)
   - chunk with Chonkie `RecursiveChunker`
   - tag: controlled metadata + **model-generated concept tags** (this is what
     surfaces connections nobody thought to list)
   - embed → Pinecone

3. **Re-ingest everything** at consistent settings. Settle chunk size
   deliberately; `.env` (1000) and code (1800) currently disagree.

4. **Fix retrieval** — the original complaint:
   - remove collection walls; retrieve across domains
   - raise `top_k` from 5 to ~15–20
   - automatic routing so users never pick a "focus area"
   - enrich personas with the framework mappings

5. **Reconcile config** so `.env`, code defaults, and docs agree.

6. **Clean up** duplicate `/sync-status` routes; archive the ~11 competing
   markdown files in the repo root.

## Deferred, deliberately

- **Revoke the GitHub token in `tac-1`/`tac-2`** — a Personal Access Token is
  embedded in plaintext in their git remotes. Not Karre's; from a tutorial.
- **Regenerate her GitHub token** with `repo` scope only; current one has
  `delete_repo` and `admin:org`.
- **`PHONE_CAMERA_BACKUPS` (52 GB)** — mislabeled. 37 GB photos + 14 GB old
  Downloads backup holding 316 documents and website source. **Do not delete**;
  needs a careful session. Excluded from ingestion.
- **The other 7 home-directory repos** — never inspected. The DreamWeaver trio
  needs the same "which is real?" investigation this project needed.
- **Missing droplet SSH key** — `~/.ssh/config` points at `~/.ssh/id_rsa`, which
  does not exist. Deployment will need a new keypair added via the DigitalOcean
  console.
