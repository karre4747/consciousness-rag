# CLAUDE.md — Agent Orientation

> Read this first. For the product vision, team, and business context, read
> `PROJECT_CONTEXT.md`.
>
> **Last verified: August 17, 2026.** Everything below was checked against the
> running system on that date. Re-verify before trusting any number.

## What this is

A RAG knowledge base for consciousness education — recovery, metaphysics,
neuroscience, and therapeutic modalities. It is **infrastructure**, not an app:
Sage (the in-app assistant), DreamWeaver Vision, and future course tooling are
all clients of this one library.

## Verify state before assuming

Documentation rots. Run these instead of trusting prose:

```bash
cd ~/Developer/consciousness-rag/backend

sqlite3 consciousness.db "SELECT status, COUNT(*) FROM documents GROUP BY status;"

./venv/bin/python -c "
import os; from dotenv import load_dotenv; load_dotenv('.env')
from pinecone import Pinecone
i=Pinecone(api_key=os.getenv('PINECONE_API_KEY')).Index(os.getenv('PINECONE_INDEX_NAME'))
print(i.describe_index_stats())"
```

## Layout

```
~/Developer/consciousness-rag/     ← the repo (git, branch: agentic-version)
├── backend/          main.py, database.py, tagging.py, .env, consciousness.db
│   ├── agents/       BaseAgent + 7 specialists
│   ├── skills/       semantic_search, metadata_filter, citation_builder
│   ├── prompts/      *_persona.txt
│   └── collections/  collections.yaml
├── library/          source PDFs (repo root, NOT under backend/)
├── mcp-server/       MCP connector for Claude Desktop ("evolveAI")
└── tools/            inventory.py, known_authors.py, dedupe.py

~/Developer/Archive/               ← superseded folders, safe to ignore
~/Developer/_backups/              ← .env, DB, and git bundle backups
```

Paths are all relative to `__file__`; the repo can be moved as a unit.

## Configuration reality

`.env` wins at runtime and **disagrees with both the code defaults and the old
docs**. Trust `.env`:

| Setting | `.env` (live) | `main.py` default | `tools/ingest.py` |
|---|---|---|---|
| Chunk size | 1000 (chars) | 1800 (chars) | **1500 (tokens)** |
| Dimensions | 3072 | 1536 | — |
| Index | `evolve-consciousness-v3` | — | reads `.env` |
| Embeddings | text-embedding-3-large | — | reads `.env` |

**Three chunk sizes are live and disagree**, in two different units. 1500 tokens
is the settled intent but exists only as a hardcoded constant in `ingest.py:42`.
`main.py` also keeps a separate `chunk_text()` at line 444 that the new pipeline
does not use. Reconciling these is the top open task — see `STATUS.md`.

## How retrieval works now

`BaseAgent.query()` calls `skills/multi_angle.py`, not a single search.

A lone semantic search returns passages closest to the question's *dominant
wording*. Ask for "CBT/DBT, the neuroscience behind it, and how step work
integrates" and CBT wins the embedding: you get therapy passages, one thin
science hit, and almost no step work — so the answer cannot braid traditions the
library actually holds.

`multi_angle_search()` therefore runs the literal question **plus one search per
domain** (recovery / science / therapy / spiritual), then merges: dedupe by
vector id keeping the best score, then round-robin across source documents so no
single verbose book fills every slot.

Measured on that exact request: **8 documents → 15**, and science coverage
1 chunk → 5.

Two things that matter when editing this:

- Domain phrasing must **lead** the angle string. Appending it to the full
  question barely moves the embedding — all angles then land in the same place.
- **Collections no longer filter retrieval.** They are a lens on voice only.
  Never reintroduce `get_pinecone_filter` into the query path.

## Known problems

**1. SQLite and Pinecone are out of sync.** `tools/ingest.py` writes vectors to
Pinecone but never updates `consciousness.db`:

| | SQLite | Pinecone |
|---|---|---|
| Documents | 65 | **346** |
| Chunks | 7,348 (deleted vectors) | **40,335** |

Retrieval is unaffected — it queries Pinecone directly. But anything reading
SQLite is wrong: the MCP `list_documents` tool, the UI document list, and status
or spending logic all report the pre-ingest library. `main.py` has a
`sync_database_with_pinecone()` suggesting this has recurred before. Decide which
store is authoritative; Pinecone holds vectors *and* metadata, so SQLite is
arguably just a listing cache.

**2. `skills/metadata_filter.py` builds filters from filenames on disk**, and
`library/` vs. Pinecone are nearly disjoint sets. No longer in the query path
(see above), but the module is still present and would reintroduce the bug if
wired back in.

**3. Collections act as walls** — **FIXED** (commit `9ab9066`).

**4. `top_k=5`** — **FIXED** (commit `9ab9066`). Now 15 in `main.py:359`,
`main.py:967`, `BaseAgent.query()`, and `mcp-server/server.py`. It was set in
four places; changing only the agent silently did nothing because `main.py`
re-defaulted it.

**4. `consciousness_level` metadata is unusable** — ~150 free-form values the
tagging model invented (e.g. "Awareness of stress influences on animal
behavior"). `recovery_focus` and `primary_chakra` ARE controlled and work as
filters.

**5. `consciousness_level` metadata is unusable** — ~150 free-form values the
tagging model invented (e.g. "Awareness of stress influences on animal
behavior"). `recovery_focus` and `primary_chakra` ARE controlled and work as
filters. New ingestion writes a tight shape instead: `concepts`, `practice`,
`evidence_base`.

**6. Duplicate routes.** `/sync-status` and `trigger_sync` are each defined
twice in `main.py`; FastAPI silently keeps the first.

## Pinecone gotchas, learned the hard way

- **Vector ids must survive `fetch()`.** Ids containing spaces or `::` upsert and
  query fine but return *nothing* from `fetch()`, making them invisible to a
  backup export — silent data loss. `tools/ingest.py:safe_id()` restricts ids to
  `[A-Za-z0-9._-]`.
- **`delete(filter=...)` silently does nothing** on this index. The call
  succeeds and removes zero vectors. Delete by explicit id. Check any deletion
  code in `main.py` against this.
- **`index.list()` yields `ListItem` objects, not strings.** Passing them
  straight to `fetch()` returns nothing. Use `getattr(item, "id", item)`.
- **Stats lag by minutes.** `describe_index_stats()` is not a reliable check
  after a write or delete; enumerate ids instead.

## MCP server

Ported to **mcp 2.x** (`MCPServer`, `@app.tool()` decorators,
`run_stdio_async()`). The 1.x `Server` / `@app.list_tools()` / `@app.call_tool()`
API was removed in 2.0. Requests are wrapped in `asyncio.to_thread` — the old
code called `requests.post` directly inside async handlers, blocking the event
loop for up to 120s per query.

Claude Desktop launches MCP servers **only at startup**: after any change, quit
(Cmd+Q) and reopen. The server also needs the backend running on port 8001.

## History worth knowing

**The corpus was deleted over a misdiagnosis.** MCP queries were timing out.
The cause was a 30-second MCP timeout against 60–90s Claude generation
(`archive/HANDOFF_MCP_PERFORMANCE_FIX.md`). Chunk size was blamed anyway, and
100+ documents were removed from Pinecone. The data was likely fine.

*Verify a diagnosis before acting on a destructive remedy.* Re-ingesting is
cheap; a curated corpus is not.

A separate, real problem — PDFs read as binary garbage — was correctly fixed
earlier with proper text extraction.

## Conventions

- **`-pdf.pdf` suffix means OCR'd** from an image. Always prefer these; the
  non-OCR twin may have zero extractable text. `tools/dedupe.py` scores for this.
- **BHBY** = Dispenza, *Breaking the Habit of Being Yourself*.
  **POSM** = Joseph Murphy, *The Power of the Subconscious Mind*.
  **CT / CTHandbook / Rays of the Dawn** = Thurman Fleet, Concept Therapy.
- **Own content vs. source**: worksheets on recovery topics are Karre's own;
  worksheets on other topics were purchased and are legitimate sources.
  `Module`, `WEEK`, `90-Day`, `Breaking Free`, `Fred` → hers.
- Never ingest from `Downloads/_ORGANIZED/PHONE_CAMERA_BACKUPS` — mislabeled
  business backup, and it contains a symlink loop that traps directory walks.

## Working agreements

- Verify with a command before stating system state.
- Copy rather than move; keep originals until a change is proven.
- Back up `.env` and `consciousness.db` before structural work — neither is in git.
- `library/` is the master copy. Pinecone is derived and rebuildable.
