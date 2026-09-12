# Course Repo — GitHub Pull Requests for Agentic Coders

Static learning-page site for the six-week cohort course. This repo holds the course
source documents (mission, mastery-objectives workbook, ADRs) and the student-facing
HTML lessons built from them. It is also **dogfooded**: the workflow the course teaches
is the workflow used to build it, so its own issues and PRs are teaching exhibits.

## Language

### Curriculum

**Mastery Objective**
: One numbered row (M01–M36) in the objectives workbook: a single assessable capability
  with a Week, Category, Bloom Level, Assessed By, and Primary Source.
  _Avoid_: learning goal, outcome.

**Learning Page**
: A self-contained, student-facing HTML lesson that teaches exactly one Mastery
  Objective (a dense objective may be covered by several Learning Pages, each still
  targeting only that objective).
  _Avoid_: article, module.

**Week Hub**
: The per-week index page: theme, objective table, assigned sources, time estimate,
  and links to that week's Learning Pages.

**Course Home**
: The site's root index page linking to Week Hubs.

**Self-Check**
: The Bloom-matched practice block ending every Learning Page: reveal-answer questions,
  plus a hands-on checklist on Apply pages.
  _Avoid_: quiz (reserved for the two graded concept quizzes).

**Checker**
: A `gh`-CLI script that reads a student's repo state and verifies the factual half of
  an assignment (branch named correctly, PR links its issue, checks passed, issue
  auto-closed on merge). It grades evidence, never judgment.

### The three repos

**Course Repo** (`perro-ruidoso/gh-pr-mastery`)
: This repo. Content, objectives, ADRs, site. Dogfooded.

**Seed Repo** (`flashcards-seed`)
: The template each student instantiates as their own private-practice substrate: a
  Python spaced-repetition flashcard CLI with layered domain/storage/CLI code, pytest,
  ruff, CI, `CLAUDE.md`, `CONTEXT.md`, and a prepared backlog of ~15 issues carrying
  real blocking edges and plantable bugs.
  _Avoid_: starter, boilerplate.

**Upstream Repo** (`flashcards-upstream`)
: The single shared repo students contribute to and take turns maintaining. Two distinct
  modes run against it, and the distinction is load-bearing — see `adr/0004`:
  **write-access mode** (students push branches directly; secrets exist; agentic CI review runs)
  and **fork mode** (students contribute from a fork; secrets are withheld; a human maintainer reviews).

**Instance**
: One student's copy of the Seed Repo.

### Work

**Work Dependency**
: A blocking relation between two units of work — ticket B cannot start until ticket A
  lands. Declared as a `/to-tickets` blocking edge, recorded on GitHub as an **Issue
  Dependency**, and drawn as a Mermaid graph. This is what this course means by
  "dependency."
  _Avoid_: "dependency" unqualified when the supply-chain graph is meant — say
  **package dependency** for that; it is out of scope.
  _Avoid_: calling it a Sub-Issue. The two are different features and the difference is
  load-bearing — see below.

**Issue Dependency**
: GitHub's mechanism for recording that one issue blocks another. A **graph**: an issue may
  be blocked by many issues and block many. This is where a Work Dependency lives.
  There is no `gh issue edit` flag for it as of `gh` 2.92.0; it is reached through
  `gh api repos/O/R/issues/N/dependencies/blocked_by`, whose payload takes the blocker's
  **database id**, not its issue number.

**Sub-Issue**
: GitHub's mechanism for breaking one issue into children. A **hierarchy**: an issue has at
  most one parent, up to eight levels deep. Good for decomposition, and structurally unable
  to express a Work Dependency where a ticket has two blockers — the Seed Repo's backlog
  has five such joins, which is the concrete reason the two mechanisms are not
  interchangeable. Reached with `gh issue edit --add-sub-issue`.

**Tracer-Bullet Ticket**
: A ticket that crosses every layer of the app and emits observable feedback, rather
  than completing one layer horizontally.

**Stacked PR**
: A pull request whose base is another open PR's head branch, expressing a work
  dependency in code. Needs retargeting when its parent merges.

**Ready-for-Agent**
: A ticket specified well enough that a fresh Claude Code session can execute it with no
  further human context. One of the five triage labels.

### Review

**Finding**
: One item reported by an automated review (`/code-review` or the Claude GitHub Action),
  before a human has judged it. A finding is a candidate, not a defect.
  _Avoid_: treating findings and defects as the same thing — separating them is M21.

**Verdict**
: A human's disposition of a finding: must-fix, nit, or false positive.

**Gate**
: A condition that must hold before a PR can merge — a required status check, a required
  approval, resolved conversations, a merge queue. Gates are configured, not requested.

### Sourcing

**Assigned Source**
: A reading the Week Hub assigns for that week.

**Grounding Source**
: An Assigned Source whose text was actually fetched at build time; every factual claim
  in a Learning Page must be traceable to one. Logged in `NOTES.md` with its fetch date.
  _Avoid_: reference.

**Source Tier**
: The course's trust hierarchy. Tier 1 **GitHub official docs** (`docs.github.com`, the
  `gh` manual) — GitHub is the subject here, so its docs are primary, not ancillary.
  Tier 2 **Anthropic official** (`code.claude.com`). Tier 3 **Pocock / AI Hero**
  (`mattpocock/skills`, `aihero.dev`). Tier 4 **Linear official** (`linear.app/docs`).
  Ancillary: selected practitioner material, used only where no primary source covers it.

**Capture**
: A screenshot of a vendor UI, stored under `docs/assets/shots/` with a visible
  capture-date caption. Captures are used only for surfaces with no CLI equivalent
  (rulesets, merge queue config, Linear settings) because they rot.
