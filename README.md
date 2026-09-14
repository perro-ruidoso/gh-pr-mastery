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
| [`checkers/`](checkers/) | `check_a1.py`, `check_a2.py`, and `check_a3.py` (grade repo state) and `check_site.py` (validates the site) |
| [`seed/SPEC.md`](seed/SPEC.md) | Build spec for `flashcards-seed` — layout, SM-2, the 15-issue backlog, planted bugs |
| [`seed/tools/`](seed/tools/) | `backlog.py` (the 15 tickets + topological check), `file_backlog.py` (files them as issues with dependency edges), and `waves_from_github.py` (reads the graph back from any repo and prints its waves or a Mermaid diagram) |
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
python checkers/check_a2.py --org ORG --handle H   # A2: labels, template, spec, ticket graph (needs gh 2.94.0+)
python checkers/check_a3.py --org ORG --handle H   # A3: branch names, PR bodies, closing links, the retarget, the merge commit
```

## Status

Backbone, **Weeks 1–3**, and the **Seed Repo** are complete and validated:
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
[`NOTES.md`](NOTES.md); the second was accepted, and the checker now grades the four
labels a student creates and only notes that `wontfix` is present.

**Week 2** (M07–M12) adds twelve Learning Pages under `docs/week-02/`, `assignments/a2.md`,
and `checkers/check_a2.py`. Its transcripts were captured with `gh` 2.100.0 — the June 2.94.0
release made issue types, sub-issues, and dependencies first-class flags, so Week 2 requires
2.94.0 or later. Two findings shaped it: a fresh Instance has **zero issues** (a template copies
files, not issues), so A2 has students build their own backlog and the Seed Repo's fifteen
tickets are the exhibit; and GitHub **accepts a dependency cycle**, so the checker runs its own
topological sort. The M11 pages carry a live experiment showing that a second `--add-sub-issue`
moves a parent rather than adding one. M12 is written for Linear's Free plan on documentary
evidence and says on the page that the UI walk has not yet been captured.

**Weeks 1 and 2 were audited on 2026-09-13** (issue #15, PR to follow) with the tools live:
every source URL re-fetched and every quotation re-checked against the fetched text, every
`gh` transcript re-run on the installed `gh` 2.100.0, both checkers fault-injected rule by
rule, and every page render-tested in Chrome at 1200 px and 400 px. What it found and fixed
is in `NOTES.md` under "Week 1–2 audit"; the short version is that `cli/cli#14398` (the M02/M04
example) closed unmerged the same morning, M06's snapshot of this repository had gone stale,
one quoted GitHub Docs sentence had been rewritten upstream, a checker regex accepted an empty
flashcard face, and 81 of 93 self-check questions gave the answer away by option length.

**Week 3** (M13–M18) adds fourteen Learning Pages under `docs/week-03/`, `assignments/a3.md`,
and `checkers/check_a3.py`. Every transcript comes from actually doing the week on a throwaway
Instance (`perro-ruidoso/flashcards-w3probe`, private, 2026-09-13): two tickets with a blocking
edge, branches from `gh issue develop`, a stacked PR whose `Closes #n` stayed empty until it was
retargeted to `main`, a diff that grew after the parent's squash merge and shrank after a
rebase, a deliberately authored drive-by PR that was closed and split, a genuine two-file
conflict resolved by running `/resolving-merge-conflicts` (its five steps are quoted and each
step's real output shown), and issues that closed themselves one second after each merge. Two
probes settled a question the docs leave ambiguous: `gh pr merge --delete-branch` on a parent
**closes** the stacked child, while the repository's *Automatically delete head branches*
setting **retargets** it. The course repo's own #12 → #14 stack is the second exhibit, with
timestamps. `check_a3.py` grades the evidence (branch named from its issue, four PR headings, the
`BaseRefChangedEvent`, a two-parent commit, the one-second close) and was fault-injected 13/13.
M18 quotes each installed skill's description verbatim and records that `request-refactor-plan`
was removed upstream on 2026-08-05.

**Weeks 1–3 were audited on 2026-09-14** (issue #19; PR stacked on #18, itself stacked on #16) the
same way, plus a cross-week coherence pass no audit had done. All 105 source URLs still answer
200; every quotation is present. What it found: the installed skills the pages quote are a
2026-07-09 snapshot, and the plugin students install has drifted further than the 13th recorded —
`qa` was retired with `request-refactor-plan` (the changeset names both replacements), the plugin
carries 25 skills and lacks two of M18's six, and `ask-matt` now reverses its `/handoff`-versus-
`/compact` advice; nine links to files outside `docs/` were 404 on the published site (fixed, and
`check_site.py` now refuses them); M06's course-repo snapshot had gone a day stale (four recorded
edges now, and a second stacked PR caught in its *before* state); M01 said the Seed's backlog is
inherited (it is not). Checkers fault-injected 28/28, 16/16, and 22/22; 42 pages render clean at
1200 and 400 px; 133 self-checks, 0 flagged. Three decisions are owed and listed in `NOTES.md`:
pin or track the plugin, what replaces `request-refactor-plan` in M18, and what M24 names instead
of `/qa`.

Not yet built: Weeks 4–6, the Upstream Repo, the Week 4 planted-bug diff (it has to be
authored on an Instance where T03 has landed, not against the template), the
merge-strategy simulator widget (Week 5), and the UI captures.

## Teaching it

[`instructors/instructor-guide.md`](instructors/instructor-guide.md) stands the course up
and teaches Week 1: org and toolchain setup, the four decisions owed before students
arrive, a 90-minute session plan with verified live demos, and how to run and calibrate A1.
[`instructors/student-setup.md`](instructors/student-setup.md) is the pre-Week-1 handout,
written to be sent to students verbatim.
