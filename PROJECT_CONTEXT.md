# Project Context — Vision, Team, Product

> The "why" behind the technical decisions. Changes slowly. For system state
> and known bugs, see `CLAUDE.md`.
>
> Last updated: August 16, 2026

## What is being built

A **general consciousness library** — not an addiction tool with other material
attached. The nearest comparison is Crystalinks: a body of knowledge people
enter from many directions. Therapists, life coaches, spiritual coaches, and
recovery sponsors should each find it equally theirs.

Addiction recovery is the **first vertical**, because it is Karre's expertise
and the fastest path to launch — not because it is the center.

The thesis: **many traditions describe the same ascent in different
vocabularies.** The product's value is surfacing connections a practitioner
could not find alone — e.g. that reading a Fourth Step inventory and
neuroplasticity research describe the same mechanism.

Long-term goal is bigger than addiction: shared frameworks for understanding
transformation, toward less fragmentation and more unity.

## The ecosystem

The library is infrastructure. These are its clients:

| Product | Role |
|---|---|
| **Sage** | In-app assistant / digital coach. Primary consumer of this library. |
| **DreamWeaver Vision** | Sponsorship app — sponsor and sponsee sides, assignments, check-ins. |
| **Wisdom Path Navigator** | Coaching/client platform. Built after trialing ~15 platforms; none combined the needed features. |
| Journaling app | Entry tier. |
| Meditation app | Second tier; includes journaling. |
| Full recovery app | Top tier; includes both. |

Tiered upgrades, with client content persisted in Supabase. Indicative pricing:
sponsors ~$20/mo for 6 sponsees, scaling to ~$38–48/mo unlimited. Deliberately
low — breadth of access is the goal.

Later: a **treatment center directory** with live bed availability, filterable
by affordability. Requires coordination with centers; starting in Texas.

## Team

Four practitioners, each a distinct lens on the same corpus:

- **Karre** — subconscious/addiction expertise; doctorate student in natural
  medicine (Quantum University); 200hr yoga teacher training. Blends all domains.
- **Julie** — licensed mental health therapist (NJ, pursuing TX); 500hr yoga
  teacher training.
- **Erica** — doctorate student in natural medicine (Quantum University); 500hr
  yoga teacher training; well-known Texas teacher, retreats; specialist in the
  quantum field and layers of subtle energy.
- **12-Step colleague** — sponsors many; supplements the Steps with metaphysics
  and heavy use of Joe Dispenza's work.

These four are the first test of practitioner framing: the same query should
answer in clinical language for Julie and energetic language for Erica.

## Framework mappings

Cross-tradition parallels that **no keyword or embedding will find**, because
the texts share no vocabulary and never cite each other. These are asserted in
`tools/known_authors.py` so ingestion can write them into metadata.

The shared spine, root → crown:

| Chakra | Steps | Theme |
|---|---|---|
| Root | 1 | survival; powerlessness; first vibration into matter |
| Sacral | 2 | desire; coming to believe; emergence of life |
| Solar plexus | 3 | will; turning it over; individuation |
| Heart | 4–5 | inventory; defects → opposing assets; self-honesty |
| Throat | 6–9 | expression; amends; readiness |
| Third eye | 10–11 | insight; meditation; pineal activation |
| Crown | 12 | awakening; remembering; service |

**Thurman Fleet / Concept Therapy** is the keystone example: his body/mind/soul
law and defects-to-opposing-assets practice run parallel to the Fourth Step, and
his creation arc (first vibration → matter → microorganism → human) parallels
the chakra ascent. Nothing in either literature says so.

**Still to be added** (revisit these mappings as material lands):
sacred geometry; **CRM therapy** (eye positions, pineal activation);
**astrology**, expected to play a large role.

## Content policy

- **Source material** → `library/`, ingested and citable.
- **Karre's own content** (course modules, recovery worksheets, client packets)
  → `my_content/`, deliberately **excluded** from retrieval for now. Including it
  would make the system cite her work back to her as an independent source, and
  would contaminate insight while she writes new curriculum. Expected to become
  available later behind an explicit flag, for voice consistency and
  cross-referencing her own modules.
- Academia.edu subscription bundles are pre-filtered by her search parameters
  and are trusted as relevant.

## Open product questions

- **Practitioner framing**: configured per professional ("I'm a therapist") vs.
  inferred per question. Configured is predictable and sellable; inferred is
  better UX but will sometimes guess wrong.
- **Safety layer for Sage**: this is a recovery population. Questions will touch
  relapse, crisis, and suicidal ideation. Sage needs crisis recognition that
  surfaces human help rather than a synthesized lesson. With a licensed
  therapist on the team and clinical protocols (CBT/DBT/EMDR) entering the
  corpus, Julie should draw the line between education and practicing therapy —
  **before launch, not after**.
- **Scope risk**: seven interconnected products. The library is what everything
  else depends on and is closest to working; finishing it first makes every
  downstream app easier.
