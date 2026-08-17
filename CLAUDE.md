# CLAUDE.md — Agent Orientation

> Read this first. For the product vision, team, and business context, read
> `PROJECT_CONTEXT.md`.
>
> **Last verified: August 16, 2026.** Everything below was checked against the
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

| Setting | `.env` (live) | `main.py` default | Old docs claim |
|---|---|---|---|
| Chunk size | 1000 | 1800 | 1800 |
| Dimensions | 3072 | 1536 | 1536 |
| Index | `evolve-consciousness-v3` | — | `evolve-consciousness` |
| Embeddings | text-embedding-3-large | — | ada-002 |

Reconciling these is an open task.

## Known problems

**1. Agents cannot see most of the library.** `skills/metadata_filter.py`
builds Pinecone filters from *filenames found on disk* in `library/`. But
`library/` and Pinecone hold nearly disjoint sets — only ~9 of 65 ingested docs
exist as files there. Most documents are unreachable by any specialist agent.

**2. Collections act as walls.** Each agent is filtered to one collection, so
`RecoveryAgent` structurally cannot retrieve neuroscience and `ScienceAgent`
cannot retrieve inventory practice. This makes the library's core promise —
cross-domain synthesis — impossible. `SynthesisAgent` passes an empty filter and
is the only one that works as intended. **That should be the default.**

**3. `top_k=5` at ~1000-char chunks** gives ~5k characters to answer from. Too
thin for synthesis regardless of retrieval quality.

**4. `consciousness_level` metadata is unusable** — ~150 free-form values the
tagging model invented (e.g. "Awareness of stress influences on animal
behavior"). `recovery_focus` and `primary_chakra` ARE controlled and work as
filters.

**5. Duplicate routes.** `/sync-status` and `trigger_sync` are each defined
twice in `main.py`; FastAPI silently keeps the first.

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
