# Spec — `flashcards-seed`, the Seed Repo

The template every student instantiates in M01 and works in for six weeks. This file is
the build spec; it exists so the seed repo can be built in a fresh session with no memory
of the conversation that designed it.

Read alongside `MISSION.md`, `CONTEXT.md`, `NOTES.md`, and `adr/0002` (why Python).

---

## 1. Role, and the one rule that matters most

The Seed Repo is a **substrate, not a subject**. Students are assessed on the workflow
around the diff, not on the code. It therefore needs: layered structure so "vertical
slice" tickets genuinely cross layers, fast deterministic tests so Week 5's required-check
and merge-queue lessons do not stall, and arithmetic subtle enough to hide a real bug.

### MUST NOT ship

These are produced **by the student** in M05, and `checkers/check_a1.py` verifies they
appear. If the template ships them, Assignment A1 becomes vacuous — every student passes
on day one without ever running the skill.

- ❌ `docs/agents/issue-tracker.md`
- ❌ `docs/agents/triage-labels.md`
- ❌ `docs/agents/domain.md`
- ❌ An `## Agent skills` section inside `CLAUDE.md`
- ❌ The five triage labels (`needs-triage`, `needs-info`, `ready-for-agent`,
  `ready-for-human`, `wontfix`) — students create them with `gh label create`.
  **Caveat, verified 2026-09-12:** `wontfix` is in GitHub's default label set and lands on
  every new repository regardless of the template, so only four of the five are actually
  withheld. Nothing the template does can change that; see `NOTES.md`.
- ❌ `a1-writeup.md`

### MUST ship

- ✅ `CLAUDE.md` — project instructions, **without** the `## Agent skills` section
- ✅ `CONTEXT.md` — the domain vocabulary in §3, which M05 tells students already exists
- ✅ A working thin tracer bullet (§4) with green tests and green CI
- ✅ The 15-issue backlog (§6) — as issues, created after the repo exists
- ✅ Repository marked as a **template**, **public**, in the course org

---

## 2. Stack

| | |
|---|---|
| Language | Python — see `adr/0002` |
| Tests | `pytest`, with `freezegun` or an injected clock (§5) |
| Lint/format | `ruff` (both linter and formatter) |
| Types | `mypy` on `src/` only, non-blocking at first |
| Packaging | `pyproject.toml`, `src/` layout, installable with `pip install -e ".[dev]"` |
| Pre-commit | the Python `pre-commit` framework — **not** Husky/lint-staged |
| CI | GitHub Actions: ruff + pytest on every PR |

**Pin CI to a Python with settled wheel availability — deliberately not the newest.**
The authoring machine runs 3.14.4, which is ahead of where CI should sit. Confirm ruff,
pytest, and freezegun all have wheels for the chosen version before committing to it, and
record the choice in `NOTES.md`. Target: full CI run well under 60 seconds.

---

## 3. Domain vocabulary

Goes in `CONTEXT.md`. M05's learning page already promises students these four terms.

**Card** — one prompt and its answer, plus the review state that schedules it.
**Deck** — a named collection of Cards, persisted as one file.
**Grade** — the 0–5 quality score a student gives their own recall of a Card.
**Interval** — whole days until a Card is next due.
**Ease Factor** — a per-Card multiplier that lengthens or shortens future intervals.
**Repetition** — the count of consecutive successful reviews of a Card.
**Due** — a Card whose next-review date is today or earlier.

---

## 4. Module layout

Three thin layers. The boundaries are the point: a tracer-bullet ticket should have to
touch all three, and a horizontal ticket should feel wrong.

```
src/flashcards/
  domain/
    models.py      # Card, Deck — dataclasses, no I/O
    scheduler.py   # SM-2. Pure functions. No clock, no files.
    stats.py       # aggregation over review history
  storage/
    json_store.py  # load/save a Deck to disk
    csv_io.py      # import/export
  cli/
    main.py        # argparse/click entry point, one function per command
tests/
  domain/  storage/  cli/
```

Rules to state in `CLAUDE.md`:

- `domain/` imports nothing from `storage/` or `cli/`.
- `scheduler.py` is **pure** — it takes the current state and a grade and returns new
  state. It never reads the clock. The caller passes `today`.
- `cli/` holds no business logic; it parses, calls, and formats.

That last rule is what makes the planted bugs (§7) reviewable — the arithmetic is in one
small, pure, well-named place, so a reviewer has no excuse.

### What ships working (the tracer bullet)

Enough to be a real program on day one, and no more:

- `Card` with `id`, `front`, `back`; `Deck` with `name` and `cards`
- `json_store.load_deck()` / `save_deck()`
- `flashcards list --deck <path>` — prints the cards
- Tests for all three layers; green CI

Everything in §6 is then genuinely open work.

---

## 5. SM-2, exactly

Grounded in the original algorithm as published by SuperMemo
(<https://super-memory.com/english/ol/sm2.htm>, fetched 2026-09-12). Implement it
faithfully — the teaching value depends on the reference behaviour being correct.

**Grades** — 5 perfect · 4 correct after hesitation · 3 correct with serious difficulty ·
2 incorrect, answer seemed easy · 1 incorrect, answer remembered · 0 complete blackout.

**Intervals**

```
I(1) := 1
I(2) := 6
I(n) := I(n-1) * EF     for n > 2
```

**Ease factor update**, applied after every review:

```
EF' := EF + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
if EF' < 1.3 then EF' := 1.3
```

**Failure** — *"If the quality response was lower than 3 then start repetitions for the
item from the beginning without changing the E-Factor."* So `q < 3` resets the repetition
count (next interval is 1 day) and **leaves EF untouched**.

**Starting EF** is 2.5.

### Two decisions the original leaves open

Record both in an ADR inside the seed repo, because they are the sites of two planted bugs:

1. **Rounding.** `I(n)` is a float. Round **half-up to the nearest integer**, with a floor
   of 1 day. State it explicitly; do not leave it to `round()`, whose banker's rounding
   gives 2 for `round(2.5)`.
2. **Clock.** `scheduler` never reads the clock. `cli` obtains `today` once per session
   and passes it down, so tests freeze time by passing a date rather than patching.

---

## 6. The backlog — 15 tickets with real blocking edges

These are created as GitHub issues after the repo exists. **The dependency structure must
be genuine**, because Week 2's dependency-graph objectives (M10, M11) and Week 3's stacked
PRs (M16) read it, and the Week 5 sequencer exercise asks students to derive the waves.

| ID | Ticket | Layer | Blocked by |
|---|---|---|---|
| T01 | Add review state to `Card`: repetitions, ease factor, interval, due date | domain | — |
| T02 | Persist review state in the deck file | storage | T01 |
| T03 | SM-2 scheduler: next interval and ease update | domain | T01 |
| T04 | `review` command: one card, prompt, grade, schedule | cli | T02, T03 |
| T05 | Due-date filtering — select only cards due today | domain | T03 |
| T06 | `review --limit N` | cli | T04, T05 |
| T07 | Tag field on `Card` | domain | T01 |
| T08 | Tag persistence in the deck file | storage | T07, T02 |
| T09 | `add` command with `--tags` | cli | T08 |
| T10 | `review --tag <tag>` | cli | T09, T06 |
| T11 | Session stats aggregation | domain | T02 |
| T12 | `stats` command | cli | T11 |
| T13 | `stats --by-tag` | cli | T12, T08 |
| T14 | CSV import, including a tags column | storage | T08 |
| T15 | `export --format json\|csv` | cli | T14 |

**Parallel-safe waves** (the answer key for the sequencer exercise — keep it out of the
seed repo itself):

```
wave 1  T01
wave 2  T02  T03  T07
wave 3  T04  T05  T08  T11
wave 4  T06  T09  T12  T14
wave 5  T10  T13  T15
```

Note the five two-parent joins — T04, T06, T08, T10, T13. Those are what make the graph
worth drawing rather than a list. T13 depending on both T12 and T08 is the clearest
example of why a linear reading of the backlog misleads: T13's ticket number sits next to
T12's, but its other parent is six tickets away in a different layer.

The graph is a DAG with a maximum parallel width of 4, which is the number the Week 5
sequencer exercise is really about — at wave 3 there are four tickets that could each go
to a concurrent agent session. Verify any edit to this table with a topological sort
before committing it; the waves above were machine-checked, not eyeballed.

### Issue body shape

Every ticket carries what M07 demands, so the backlog is also a worked example of the
standard students are held to:

```markdown
## Context
Why this exists, in two sentences.

## Acceptance criteria
- [ ] Observable, checkable statements
- [ ] Including the test that must exist

## Out of scope
Explicitly, what this ticket does not do.

## Blocked by
#<n> — and why
```

Declare blocking edges as **GitHub issue dependencies**, not only prose, so that M11 has
something real to read.

> **Corrected 2026-09-12.** This paragraph originally said "sub-issue / blocking
> relations", conflating two different features. A sub-issue relation is a *hierarchy* —
> one parent, many children — and therefore cannot express this graph at all, because five
> of these fifteen tickets have two blocking parents. Issue **dependencies** are the right
> mechanism, and they are a separate REST API with no `gh issue edit` flag:
>
> ```
> POST /repos/{owner}/{repo}/issues/{n}/dependencies/blocked_by  {"issue_id": <db id>}
> ```
>
> `issue_id` is the database id, not the issue number. Verified live; see `NOTES.md`.

---

## 7. Planted bugs — for the Week 4 review drill

**These do not live on the template's default branch.** The template's `main` is green and
correct. The planted bugs ship as a **prepared pull request** (or a patch file the
instructor applies to each Instance) so that M21's `/code-review` exercise and M22's
peer-review exercise have a real diff with known defects.

All three survive a naive test suite, and all three are findable by reading
`scheduler.py` against §5:

1. **Ease floor applied in the wrong order.** Clamp to 1.3 *before* applying the update
   rather than after, so EF can end below the floor after a run of low grades. Tests that
   only check a single review pass.
2. **Failure resets the ease factor.** On `q < 3`, reset repetitions *and* set EF back to
   2.5 — contradicting the "without changing the E-Factor" rule. Invisible unless a test
   drives a fail-then-recover sequence.
3. **Banker's rounding.** Use bare `round()` for the interval, so `round(2.5)` yields 2
   instead of 3. Off by one day, only on exact halves, only sometimes.

Each bug should also have a **decoy**: at least one `/code-review` finding that is a
genuine nit or a false positive, so M21's "separate verified findings from noise" has
something to separate. Do not curate the agent's output — run it and use what it says.

---

## 8. Repository settings

- **Public**, in the course org (`adr/0003` — this is a curriculum requirement)
- **Template repository** flag on — M01 uses `gh repo create --template`, and
  `check_a1.py` asserts `templateRepository.nameWithOwner` equals `<org>/flashcards-seed`
- No rulesets, no branch protection, no CODEOWNERS — students configure those themselves
  in Week 5 (M26, M27) on their own Instance
- No Actions secrets — the Claude GitHub Action is instructor-funded on
  `flashcards-upstream` only (`adr/0004`)
- Issue templates: optional, but if present they must not pre-fill the acceptance criteria
  M07 asks students to write

---

## 9. Build order

1. `pyproject.toml`, `src/` layout, ruff + pytest config, CI workflow. Confirm green.
2. The tracer bullet (§4) with tests at all three layers.
3. `CLAUDE.md` and `CONTEXT.md`. Re-read §1's must-not-ship list before committing.
4. Push to the org; set the template flag; verify with
   `gh repo view <org>/flashcards-seed --json isTemplate,visibility`.
5. File the 15 issues with bodies per §6 and real blocking relations.
6. Verify the whole thing by instantiating a throwaway Instance and running
   `python checkers/check_a1.py --org <org> --handle <throwaway>` — it should fail on
   exactly the student-produced items (`docs/agents/*`, labels, write-up) and pass on
   repo shape. **If it passes the `docs/agents` checks, the template is wrong.**
7. Build the planted-bug PR (§7) last, against an Instance rather than the template.

---

## 10. Open questions

- ~~Python version for CI~~ — **settled 2026-09-12: 3.12.** Wheel availability for ruff,
  pytest, and mypy was checked against PyPI; the table is in `NOTES.md`.
- ~~Whether `freezegun` is worth the dependency~~ — **settled: no.** `today` is passed
  explicitly, and the seed repo's `docs/adr/0001` records that decision alongside the
  SM-2 rounding rule. The seed ships with **zero** runtime dependencies.
- Whether the planted bugs ship as a prepared PR on each Instance or as a patch students
  apply. A PR is more realistic; a patch is less work to distribute. Decide before Week 4.
  Note that §7's bugs live in `scheduler.py`, which is **T03's** output — so the
  planted-bug diff can only be built on top of an Instance where T03 has landed, not
  against the template.
