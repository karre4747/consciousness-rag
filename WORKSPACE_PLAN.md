# Workspace Plan — how the pieces fit

> Written Aug 17, 2026. This is a **plan**, not a description of what exists.
> Nothing here is built except where marked. For system state see `STATUS.md`.

## The problem this solves

Four folder methodologies were evaluated (Life OS, iCOR, AI Impact, Van Cleef's
ICP) plus a hand-built NEURO vault. The instinct to pick "the best one" is a
trap: they are not competitors, they are different layers. Choosing between them
is what has stalled the decision.

## The four layers

| Layer | What it holds | Where | State |
|---|---|---|---|
| **Workplace** | Orchestrator + agents; where work gets done | iCOR vault | downloaded, not yet run |
| **Own knowledge** | Karre's frameworks, curriculum, synthesis | NEURO vault (124 notes) | working, plugins active |
| **Source library** | 346 books/papers she did NOT write | `~/Developer/consciousness-rag` | **built, 40,335 vectors** |
| **Code** | Backend, apps, repos | `~/Developer/` | working |

They connect rather than merge. "Everything in one place" means **one place you
start from**, not one folder containing everything.

## Why the library stays separate from the vaults

Content policy already in `PROJECT_CONTEXT.md`: material Karre wrote is excluded
from the library so the system never cites her work back to her as an
independent source. That distinction is structural, not cosmetic —

- **Library** = other people's material. Job: retrieval across 346 sources.
- **Vaults** = her material. Job: linked thinking, building on her own work.

The MCP server (`evolveAI`, already working) is the bridge. An agent working in
a vault can query all 40,335 vectors without the two stores merging.

## Sequence

**Now — finish the library.** It is closest to working and everything downstream
depends on it. Remaining: the books/articles/worksheets split, then the four
practitioner lenses. See `STATUS.md`.

**Next — run iCOR before building around it.** Talk to Larry, try one real task.
It may not fit how she works; better to find that out before migrating anything.
Do not restructure on the assumption it fits.

**Then — decide the NEURO vault's fate.** Its 124 notes either migrate into
iCOR's structure or stay separate. Needs an actual read of the contents, not a
guess.

**Later — connect the library to whichever workplace wins.** The MCP server
already exists, so this is configuration, not construction.

## What NOT to do

- Do not adopt a methodology wholesale before running it on real work.
- Do not move repos into a notes vault. Code lives in `~/Developer/`.
- Do not merge her own content into the source library; see content policy.
- Do not reorganize 4.5 GB of scattered folders while the library is unfinished.

## Note on iCOR

Not a filing convention — an operating system for agent work. Worth taking
seriously: `CLAUDE.md` boots every session; Larry orchestrates and launches
specialists as subagents; deterministic work runs through scripts while judgment
stays with the model ("code for anything a machine could tell you got wrong").
Built for entrepreneurs without time to build infrastructure, which is the stated
need.
