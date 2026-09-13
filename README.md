# GitHub Pull Requests for Agentic Coders

Source repo for a six-week, cohort-taught mastery course on running real development work
through GitHub pull requests while directing Claude Code as the implementer.

| Document | What it holds |
|---|---|
| [`MISSION.md`](MISSION.md) | Why the course exists, what a graduate can do, constraints, scope |
| [`CONTEXT.md`](CONTEXT.md) | Ubiquitous language — the terms this repo uses precisely |
| [`NOTES.md`](NOTES.md) | Verified facts with sources and fetch dates, open questions, build log |
| [`RESOURCES.md`](RESOURCES.md) | Source tiers and the specific pages each objective is grounded in |
| [`objectives/`](objectives/) | The M01–M36 mastery-objectives workbook and its generator |
| [`adr/`](adr/) | Architecture decisions, including the two that verification forced |
| [`docs/`](docs/) | The student-facing site — Course Home, Week Hubs, Learning Pages (one folder per objective), shared assets |
| [`assignments/`](assignments/) | Assignment briefs and rubrics |
| [`instructors/`](instructors/) | Instructor guide (course + Week 1 setup, teaching notes, grading) and the student setup handout |
| [`checkers/`](checkers/) | `check_a1.py` (grades repo state) and `check_site.py` (validates the site) |
| [`seed/SPEC.md`](seed/SPEC.md) | Build spec for `flashcards-seed` — layout, SM-2, the 15-issue backlog, planted bugs |
| [`seed/tools/`](seed/tools/) | `backlog.py` (the 15 tickets + topological check) and `file_backlog.py` (files them as issues with dependency edges) |
| [`roadmap/`](roadmap/) | `roadmap.docx` — what is built, what is not, what has to be decided — and the script that generates it |

## Shape

Six weeks, ~4 hrs/week, 36 mastery objectives, cohort of 8–14 with a weekly live meeting.
Standalone: assumes generic GitHub familiarity, not the "Agentic Coding with Claude" course.

| Wk | Unit | Objectives |
|---|---|---|
| 1 | The machine you work in | M01–M06 |
| 2 | Issues as units of agent work | M07–M12 |
| 3 | Branches and the shape of a diff | M13–M18 |
| 4 | Owning the diff | M19–M24 |
| 5 | Gates and automation | M25–M30 |
| 6 | The maintainer seat, PM integration, and capstone | M31–M36 |

## Three repos

- **`perro-ruidoso/gh-pr-mastery`** (this one) — course content and site, dogfooded at unit granularity
- **`flashcards-seed`** — Python spaced-repetition CLI template each student instantiates
- **`flashcards-upstream`** — shared repo students contribute to and take turns maintaining

All three are **public**; that is a curriculum requirement, not a preference
(see [`adr/0003`](adr/0003-public-repos.md)).

## Rebuilding the generated files

```bash
python objectives/build_objectives.py   # mastery-objectives.xlsx and .md
python roadmap/build_roadmap.py         # roadmap.docx
```

Each writes its outputs from a single list inside the script. **Edit the Python, never the
outputs** — a hand-edit to the `.xlsx` or the `.docx` is silently discarded by the next run.

## Validating

```bash
python checkers/check_site.py                      # links, assets, lesson structure, answer keys
python checkers/check_a1.py --org ORG --handle H   # one student's A1 repo state
```

## Status

Backbone, the **Week 1 vertical slice**, and the **Seed Repo** are complete and validated:
Course Home, the Week 1 hub, thirteen Learning Pages across M01–M06 (each objective is a
folder under `docs/week-01/` with an `index.html` entry page and one or two supporting
pages), assignment A1 with its rubric, and two checkers. Every page ends with a Self-Check,
a flashcard deck (`docs/assets/flashcards.js`), and a where-to-learn-more list whose URLs
were fetched before shipping. Every terminal transcript in the lessons was captured from a
real command run against a real repository. `objectives/mastery-objectives.md` carries a
Learning Pages column linking each objective to its pages.

[`perro-ruidoso/flashcards-seed`](https://github.com/perro-ruidoso/flashcards-seed) is
live — public, template flag set, CI green in 24 s on Python 3.12, and all 15 backlog
issues filed with 19 blocking edges recorded as real GitHub issue dependencies. The graph
was re-derived from what GitHub stores and matches `seed/SPEC.md` §6's answer key: five
waves, maximum parallel width four.

Building it turned up two problems and fixed one of them. `checkers/check_a1.py` was
reading `templateRepository.nameWithOwner`, a field `gh` does not return, so every student
would have failed the "created from template" check — now fixed. And `wontfix`, one of the
five triage labels A1 asks students to create, is a GitHub default that arrives on every
new repository, so that item assesses four labels rather than five. Both are written up in
[`NOTES.md`](NOTES.md); the second is an open question.

Not yet built: Weeks 2–6, the Upstream Repo, the Week 4 planted-bug diff (it has to be
authored on an Instance where T03 has landed, not against the template), the
merge-strategy simulator widget (Week 5), and the UI captures.

## Teaching it

[`instructors/instructor-guide.md`](instructors/instructor-guide.md) stands the course up
and teaches Week 1: org and toolchain setup, the four decisions owed before students
arrive, a 90-minute session plan with verified live demos, and how to run and calibrate A1.
[`instructors/student-setup.md`](instructors/student-setup.md) is the pre-Week-1 handout,
written to be sent to students verbatim.
