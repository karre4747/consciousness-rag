# Status & Next Actions

> Where the work actually stands. Update at the end of each session.
> Last updated: **August 17, 2026**

## Verified state, August 17

Checked against the running system, not remembered:

| Fact | Value |
|---|---|
| Pinecone `evolve-consciousness-v3` | **40,335 vectors**, **346 documents**, 3072 dim |
| Docs in `consciousness.db` | **65** — STALE, see below |
| Files in `library/` | 53 + 4 OCR'd (originals stay in source folders) |
| Files in `my_content/` | 0 (52 identified, not yet copied) |
| Chonkie | 1.7.0, `RecursiveChunker`, 1500 tokens |
| MCP server | ported to mcp 2.x, verified over a real handshake |

**The full corpus IS ingested** — 346 documents, up from 65. Ingestion ran from
the inventory's source paths directly, so files were never copied into
`library/` first; that folder is not the master copy it is described as being.
Decide whether to copy them in or accept the inventory CSV as the manifest.

**SQLite is stale and must be repaired.** `tools/ingest.py` writes Pinecone only.
Anything reading SQLite — MCP `list_documents`, the UI list, spending logic —
reports 65 documents and 7,348 chunks that no longer exist.

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

## Done — ingestion pipeline

`tools/ingest.py` implements the full path: extract → low-yield detect →
OCR/quarantine (`quarantine.json`) → clean OCR artifacts (`tools/extract.py`) →
Chonkie `RecursiveChunker` → tag → embed → Pinecone.

Collection walls removed and `top_k` raised 5 → 15 (commit `9ab9066`).

**Corpus re-ingested (Aug 17).** Index cleared after a verified 360 MB export
(`_backups/.../pinecone_export_20260816.jsonl`, 7,348 vectors, 0 malformed).
Then 342 of 351 documents ingested → 39,792 chunks. 9 quarantined by the
text-quality gate; 4 were real books (Human Energy Systems, Hearth Book,
Activate your Merkaba, IQ-501 Dispenza) recovered with `ocrmypdf` and ingested
for 543 more chunks. **Total 40,335 vectors, 346 documents.**

The other 5 quarantined files were industrial datasheets from Karre's former
electronics-recycling company — they matched on "alcohol" and "inventory".
Excluded permanently in `known_authors.py`, along with `subto` / creative-finance
material and named client notes.

**Multi-angle retrieval** (`backend/skills/multi_angle.py`) — see `CLAUDE.md`.

**MCP server ported to mcp 2.x.** Rebuilding its venv had installed mcp 2.0,
whose API removed the 1.x decorators the code used, so the server crashed at
startup with no tools. First fix was a downgrade pin; Karre correctly pushed back
that this builds for the past. Ported forward instead.

## Next actions, in order

1. **Repair SQLite, then make ingestion write it.** Two parts: backfill
   `consciousness.db` from Pinecone so the 346 documents are recorded, and add
   SQLite writes to `tools/ingest.py` so it cannot drift again. Until this is
   done, `list_documents` in Claude Desktop shows a 65-document library.

2. **Settle chunk size in ONE place.** Three values live in two units:

   | Location | Value | Unit |
   |---|---|---|
   | `tools/ingest.py:42` | **1500** | tokens ← settled intent |
   | `.env` `CHUNK_SIZE` | 1000 | characters |
   | `backend/main.py:62` default | 1800 | characters |

   The corpus is already embedded at 1500 tokens, so this is now a
   consistency/documentation fix rather than a re-embed decision — but leaving
   three values invites someone to "fix" the wrong one. Also delete the dead
   `chunk_text()` at `main.py:444` that the new pipeline bypasses.

3. **Build the four practitioner lenses** (Karre / Julie / Erica / Chad) as
   *content-creation* prompts — see the two-audience section in
   `PROJECT_CONTEXT.md`. The existing seven personas answer clients; they are the
   wrong shape for "help me build a 30-minute lecture". Enrich with the chakra ↔
   Steps ↔ Fleet mappings.

4. **Decide `library/`'s role.** Ingestion read from original source folders, so
   `library/` holds 53 files while the index holds 346. Either copy the corpus in
   (making it the master copy the docs claim) or treat the inventory CSV as the
   manifest and say so.

5. **Autostart the backend.** A LaunchAgent so port 8001 is always up. Right now
   a Mac restart silently breaks every client, and the failure looks like a
   broken system rather than a stopped process.

6. **Consider consolidating seven topic agents to four voices.** Retrieval is now
   identical across all of them, so they differ only by prompt. Fewer, broader
   voices means less drift and fewer wrong-voice outcomes. Revisit after 3.

7. **Clean up** duplicate `/sync-status` routes; archive the ~11 competing
   markdown files in the repo root.

## Start in parallel, long lead time

**Safety layer for Sage.** `PROJECT_CONTEXT.md` calls for Julie to draw the
education/therapy line **before launch, not after**. This is a conversation with
a licensed human, not a coding task — begin it now rather than discovering it
blocks release.

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
