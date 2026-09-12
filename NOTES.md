# Notes — verified facts, open questions, build log

## Verified facts

Every row was fetched from the named primary source on the date shown. Re-verify before
each cohort; the vendor-behaviour rows are the ones that move.

### GitHub plan and visibility gates — verified 2026-09-12

| Fact | Source |
|---|---|
| "You can enable branch restrictions in public repositories owned by a GitHub Free organization and in all repositories owned by an organization using GitHub Team or GitHub Enterprise Cloud." | [About protected branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches) |
| Rulesets are available in **public** repositories on GitHub Free and GitHub Free for organizations; private repos need Pro/Team/Enterprise. | [About rulesets](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets) |
| Merge queue is available in **any public repository owned by an organization**, and in private repositories only on GitHub Enterprise Cloud. Not available for private repos on Free or Team. | [Managing a merge queue](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/managing-a-merge-queue) |

**Consequence:** all three course repos are public. This is a design requirement, not a
preference - but note that the reason narrowed once the real org was created. See `adr/0003`.

### Course org - verified 2026-09-12

`perro-ruidoso`, created 2026-09-12, instructor role `admin`, state `active`.
`gh api orgs/perro-ruidoso --jq '.plan'` returns
`{"name":"team","seats":2,"filled_seats":1,"private_repos":999999}` - the org is on
**GitHub Team, not Free**. Rulesets and branch protection therefore *would* work on private
repos here; **merge queue** is the only gate that still forces public, since Team does not
have it for private repositories. `adr/0003` was revised accordingly and the reasoning in
`docs/index.html` and M01 was corrected - both had claimed a free-org limitation that does
not apply to this org.

Branch protection settings available (for M26/M28/M29 coverage): require PR reviews,
require status checks, require conversation resolution, require signed commits, require
linear history, require merge queue, require deployments, lock branch, disallow bypass,
restrict who can push, allow force pushes, allow deletions.

### Sub-issues — verified 2026-09-12

Generally available. **Up to 100 sub-issues per parent**, **up to eight levels of
nesting**. CLI support exists, which is what makes M11 teachable without the web UI:

- `gh issue create --title "T" --body "B" --parent PARENT-NUMBER`
- `gh issue edit PARENT --add-sub-issue N` / `--remove-sub-issue N`
- `gh issue edit N --remove-parent`

Source: [Adding sub-issues](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/adding-sub-issues)

### Issue dependencies are a separate feature from sub-issues — verified 2026-09-12

A sub-issue relation is a **hierarchy**: one parent, many children. It therefore **cannot**
express the Seed Repo's backlog graph, five of whose fifteen tickets have *two* blocking
parents (T04, T06, T08, T10, T13). `seed/SPEC.md` §6 originally said to declare the edges
as "sub-issue / blocking relations", conflating the two; it has been corrected.

The right mechanism is GitHub's **issue dependencies** REST API, whose routes were probed
live against `cli/cli` and whose payload was confirmed from the server's own 422:

```
GET  /repos/{owner}/{repo}/issues/{n}/dependencies/blocked_by   -> []
GET  /repos/{owner}/{repo}/issues/{n}/dependencies/blocking     -> []
POST /repos/{owner}/{repo}/issues/{n}/dependencies/blocked_by
     {"issue_id": <database id, not issue number>}
```

```
$ gh api -X POST repos/cli/cli/issues/14404/dependencies/blocked_by -f dummy=1
{"message":"Invalid request.\n\nInvalid input: object is missing required key: issue_id.",
 "documentation_url":"https://docs.github.com/rest/issues/issue-dependencies#add-a-dependency-an-issue-is-blocked-by",
 "status":"422"}
```

`issue_id` is the **database** id (`gh api repos/O/R/issues/N --jq .id`), not the number
shown in the UI. There is no `gh issue edit` flag for dependencies as of `gh` 2.92.0, so
M11 teaches `gh api` for this half — worth knowing before the M11 page is written.

### Template instantiation: what it copies — verified 2026-09-12

Established by experiment against the real org, not from the docs, because the docs are
silent on the part that mattered.

GitHub's page on creating a repository from a template says only that a template copies
"the same directory structure and files", and that "a repository created from a template
starts with a single commit". It says nothing about labels.

**Labels are NOT copied.** `wontfix` was deleted from `flashcards-seed`, a fresh instance
was then created from it, and `wontfix` was present in the new repository anyway. Every
new repository — template-derived or not — gets GitHub's current default label set:

```
accessibility  bug  documentation  duplicate  enhancement
good first issue  help wanted  invalid  question  wontfix
```

(Note `accessibility`, which is not in the classic nine.)

**Consequence for A1.** `wontfix` is one of the course's five triage labels, so students
receive it for free and `check_a1.py` genuinely assesses only **four** of the five. The
template cannot prevent this — `seed/SPEC.md` §1 lists `wontfix` under "must not ship",
and that item is unachievable by any change to the template. A1's
`gh label create ... || true` loop already swallows the collision, so nothing breaks;
the objective is just softer than intended. See the open question below.

**Also observed:** labels take a few seconds to appear on a newly created repository. An
immediate `gh label list` returned an empty set; the same call moments later returned all
ten. Graders running `check_a1.py` seconds after a student creates their Instance could
see a spurious label failure.

### Actions secrets and forks — verified 2026-09-12

> "With the exception of `GITHUB_TOKEN`, secrets are not passed to the runner when a
> workflow is triggered from a forked repository."

Source: [Using secrets in GitHub Actions](https://docs.github.com/en/actions/security-for-github-actions/security-guides/using-secrets-in-github-actions)

**Consequence:** a Claude GitHub Action review workflow **cannot** run on a PR opened
from a fork. This broke the originally-planned Week 5/6 design and forced `adr/0004`.
It is now taught deliberately as M30 — the security reason behind the limit is worth
more than the convenience it costs.

### Claude Code GitHub Action — verified 2026-09-12

- Two auth secrets: `ANTHROPIC_API_KEY` (metered API billing) or
  `CLAUDE_CODE_OAUTH_TOKEN`, "an OAuth token that authenticates with your Claude
  subscription, available on Pro, Max, Team, and Enterprise plans. Generate one by
  running `claude setup-token` locally."
- "If you authenticate with an OAuth token, runs use your Claude subscription instead of
  API billing." → the instructor's Pro subscription can fund the upstream repo's reviews.
- An OAuth token "is tied to the subscription of the person who ran `claude setup-token`";
  for org-wide secrets Anthropic recommends an API key instead. Fine here: one repo.
- The action checks the triggering actor: **must have write access**, and must not be a
  bot. So students need write access on the Upstream Repo to use `@claude` there.
- Action repo docs note: "On public repositories, GitHub withholds secrets from runs
  triggered by fork pull requests, so the review runs only on pull requests from branches
  in the same repository."

Source: [Claude Code GitHub Actions](https://code.claude.com/docs/en/github-actions)

### Claude Code Review (managed product) — verified 2026-09-12, REJECTED for this course

- "Code Review is in research preview, available for **Team and Enterprise**
  subscriptions." Students are on Pro.
- "Each review averages **$15-25** in cost," billed as usage credits.
- Reviews a fork PR **only** when someone with write access comments `@claude review`.

Rejected on both cost and plan grounds. The course uses the **Claude Code GitHub Action**
(instructor OAuth token) plus local `/code-review` instead. Revisit if the plan
requirement relaxes.

### Linear GitHub integration — verified 2026-09-12, INCOMPLETE

Two distinct capabilities confirmed:
1. **PR/commit linking** — branch names, PR titles, and magic words (`Fixes`, `Closes`,
   `Refs`, `Relates to`) drive issue status through draft/open/review/merged.
2. **GitHub Issues Sync** — bidirectional sync of title, description, status, assignees,
   labels, comments between a Linear team and a GitHub repo; "only syncs issues going
   forward."

Source: [Linear Docs — GitHub](https://linear.app/docs/github)

**OPEN:** the docs page does not state which Linear **plan** includes Issues Sync. Must
be confirmed against `linear.app/pricing` against a real Free workspace before Week 2's
M12 is written, since M12 assumes students on Free can complete the wiring. If Sync is
paid-only, M12 falls back to PR/commit linking alone (which is sufficient for the
status-automation objectives M34) and Week 6's sync content becomes instructor-demoed.

### Seed Repo toolchain pins — verified 2026-09-12

Queried against the PyPI JSON API on the build date:

| Package | Latest | `requires_python` | Wheels for 3.12 |
|---|---|---|---|
| `ruff` | 0.16.7 | `>=3.7` | yes — `py3-none-*`, interpreter-independent |
| `pytest` | 9.1.1 | `>=3.10` | yes — `py3-none-any` |
| `mypy` | 2.3.1 | `>=3.10` | yes — `cp312` wheels present (also cp310–cp315) |

**Decision: CI pins Python 3.12**; the package declares `requires-python = ">=3.10"` so
students can work on anything from 3.10 up. 3.12 is two minor versions behind the local
3.14.4 and every tool has settled wheels for it, which is what `adr/0002` asked for. Full
local suite: **20 tests in 0.18 s**, so the sub-60-second CI target has ample headroom.

`ruff` is pinned to the **exact** version in both `pyproject.toml`'s dev extra and the CI
lint job, so a student's local lint result and CI's cannot disagree — which matters once
Week 5 makes lint a required check.

Pre-commit hook ids were read from the tagged `.pre-commit-hooks.yaml` rather than
assumed: at `astral-sh/ruff-pre-commit` **v0.16.7** the ids are **`ruff-check`** and
`ruff-format`; plain `ruff` still exists but is labelled "legacy alias". Hook repo revs
pinned: `ruff-pre-commit` v0.16.7, `pre-commit/pre-commit-hooks` v6.0.0. Actions pinned:
`actions/checkout@v7`, `actions/setup-python@v7`.

### Local environment — verified 2026-09-12

`gh` 2.92.0, authenticated as `acatlin`, Python 3.14.4, git 2.52.0.windows.1.

Token scopes were `gist, read:org, repo, workflow`; after the refresh the scopes are
**`admin:org, gist, project, repo, workflow`**, so the org and Projects blockers are
cleared. `perro-ruidoso` exists (created 2026-09-12) and held **no repositories** at the
time the Seed Repo build started.

## Open questions

- Linear Free plan's Issues Sync availability (above) — blocks final wording of M12.
- **The fifth triage label is free.** `wontfix` is in GitHub's default label set, so A1
  item 4 assesses four labels, not five (verified above). Three ways out, none of them
  obviously right: accept it; rename the course's fifth role to something outside the
  defaults (`declined`?), which costs a change to `docs/agents/triage-labels.md` and the
  Pocock skill's own vocabulary; or have `check_a1.py` assert that `wontfix` was *edited*
  (description or colour changed from GitHub's default) as evidence the student handled it
  deliberately. Decide before the first cohort.
- **Org plan: pay for Team seats, or downgrade to Free?** `perro-ruidoso` was created on
  GitHub **Team** (2 seats, 1 filled). A cohort of 8-14 plus the instructor needs 9-15
  seats at $4/user/month. Downgrading to Free costs the curriculum **nothing** - every gate
  the course uses works on a public repo at either tier (see `adr/0003`). Decide before
  inviting students.
- ~~Week 1's M06 assigns students a merged PR in `gh-pr-mastery` and that repo has no PR
  history~~ — **resolved 2026-09-12.** The repo is pushed, public, and has begun being
  dogfooded; A1 item 6 now has a real target. The history is still short, and both A1 and
  M06 now say so explicitly rather than implying six units of exemplary process that does
  not exist. Keep an eye on this as the history grows: M06's claim about what the
  repository demonstrates has to stay true.
- Whether instructor's Pro subscription usage limits can absorb CI review volume for
  8–14 students, or whether Max is needed. Measure during the Week 5 dry run.

## Build log

- **2026-09-12** — Grill session completed; 21 decisions settled. Backbone built:
  `MISSION.md`, `CONTEXT.md`, `NOTES.md`, `RESOURCES.md`, ADRs 0001–0004, objectives
  workbook M01–M36. Four risky facts verified; two of them (fork secrets, Code Review
  plan gate) changed the agreed Week 5/6 design.
- **2026-09-12** — `seed/SPEC.md` written so the Seed Repo can be built cold. Two things
  in it are easy to get wrong and are called out loudly: the template **must not** ship
  `docs/agents/*`, the five triage labels, or a `CLAUDE.md` `## Agent skills` section —
  those are what A1 grades students on producing — and the SM-2 arithmetic is grounded in
  the original SuperMemo publication (fetched 2026-09-12) because the Week 4 planted bugs
  are deviations from it. The 15-ticket dependency graph was verified by topological sort:
  it is a DAG, 5 waves, max parallel width 4, five two-parent joins. That check caught an
  error in the prose (T06 was missing from the list of joins).
- **2026-09-12** — Week 1 vertical slice built end to end: `docs/assets/styles.css`
  (copied from the claude_10 design system and re-keyed to a purple accent),
  `docs/assets/app.js`, vendored `mermaid.min.js` 11.15.0, Course Home, the Week 1 hub,
  six Learning Pages M01–M06, `assignments/a1.md`, and two checkers.
  - Every `gh` transcript in the lessons was **captured by running the command**, against
    `cli/cli` on 2026-09-12 — not written from memory. The M03 two-dot/three-dot transcripts
    come from a purpose-built local repo whose four commands are reproducible.
  - The M06 worked example is `cli/cli#14404` / `#14429`: PR merged at `15:55:40`, issue
    closed at `15:55:42`. That two-second gap is the evidence that a linking keyword, not a
    human, closed the issue — the whole page is built on it.
  - `checkers/check_a1.py` grades repo state via `gh --json`; all of its gh plumbing
    (label parsing, contents endpoint hit and miss, base64 decode) was exercised against
    live GitHub. A smoke test caught a real bug (`exc.splitlines()` on an exception).
  - `checkers/check_site.py` validates internal links, asset wiring, lesson structure, and
    self-check answer keys. Verified by injecting three faults (broken link, Mermaid diagram
    with no library, `data-answer` naming a missing option) — all three were caught, then
    reverted. Currently: 8 pages, 67 internal links, clean.
- **2026-09-12** — Seed Repo built locally from `seed/SPEC.md`, green end to end, and
  staged for the org. 21 files, one commit, **zero runtime dependencies**.
  - Tracer bullet only, per §4: `domain/models.py` (`Card` frozen, `Deck`),
    `storage/json_store.py`, `cli/main.py` with `flashcards list`. `scheduler.py`,
    `stats.py`, and `csv_io.py` are deliberately **absent** — they are T03, T11, and T14,
    and shipping them would empty the backlog. §4's module tree is the target layout, not
    the shipped one; `CLAUDE.md` says which of it exists today.
  - **20 tests in 0.18 s**; `ruff check`, `ruff format --check`, and `mypy --strict` all
    clean; all seven `pre-commit` hooks pass on `--all-files`. Every one of these was run,
    not assumed.
  - The §1 must-not-ship list was audited against `git ls-files` before the commit:
    no `docs/agents/`, no `## Agent skills` heading, no `a1-writeup.md`, and none of the
    five triage-label strings anywhere in the tree. Reproduce with
    `git ls-files | grep docs/agents` and `grep -rn 'needs-triage' .` — both must be empty.
  - The 15-ticket graph was re-derived by topological sort from the ticket table before
    any issue was filed, and reproduces §6's answer key exactly: 5 waves, max parallel
    width 4, joins at T04, T06, T08, T10, T13.
  - Two spec corrections fell out of the build, both recorded above: issue **dependencies**
    rather than sub-issues carry the blocking edges (sub-issues cannot express a
    two-parent join), and the CI Python is pinned to 3.12.
  - `docs/adr/0001-sm2-rounding-and-the-clock.md` ships in the seed. It fixes half-up
    rounding and the caller-supplied clock *before* anyone writes the scheduler, which is
    what makes §7's planted bugs deviations from a written rule rather than matters of
    taste — and gives M21's reviewers something to read the diff against.
  - Org-side half of §9 completed the same day. `perro-ruidoso/flashcards-seed` is
    **public**, **template**, default branch `main`, not a fork. CI on the initial push:
    both jobs green in **24 s** on CPython **3.12.14** — 20 tests in 0.05 s, mypy strict
    clean — comfortably inside the sub-60-second budget `adr/0002` asked for.
  - All 15 issues filed (#1–#15) with **19 blocking edges** as real GitHub issue
    dependencies. The graph was then re-derived *from what GitHub stores*, by reading
    every `dependencies/blocked_by` back and running Kahn's algorithm on the result — not
    from the script that wrote it. It reproduces §6's answer key exactly: 5 waves, max
    parallel width 4, joins at T04, T06, T08, T10, T13.
  - **Step 6 caught a real bug in `checkers/check_a1.py`.** It read
    `templateRepository.nameWithOwner`, but `gh repo view --json templateRepository`
    returns `{id, name, owner{id, login}}` and no `nameWithOwner` — so the field was
    always `None` and **every student would have failed "Created from template"** on a
    correctly-created Instance. Fixed by composing `owner.login` + `name`; the checker now
    passes repo shape and fails exactly the student-produced items, which is what §9 step
    6 says a correct template must produce.
  - A second finding from the same step: `wontfix` is a GitHub default label and cannot be
    kept out of a student's Instance. Written up above; an open question now.
  - **Left over for the instructor:** two throwaway repositories,
    `perro-ruidoso/flashcards-smoketest` and `perro-ruidoso/flashcards-labelprobe`. The
    build token has `admin:org, gist, project, repo, workflow` but **not** `delete_repo`,
    so they must be removed with `gh auth refresh -s delete_repo` or from the web UI.
  - **Still not built:** §7's planted-bug diff. Those bugs live in `scheduler.py`, which
    is T03's output — so the diff can only be authored on an Instance where T03 has
    landed, never against the template. Week 4 work.
- **2026-09-12** — Course repo put under version control and pushed as
  `perro-ruidoso/gh-pr-mastery`: public, `main`, 31 files in one squashed initial commit.
  Nothing before that point had history, and none was invented. Pages enabled from
  `main /docs` per `adr/0001` and serving at
  <https://perro-ruidoso.github.io/gh-pr-mastery/>.
  - Dogfooding started. #1 (org-qualify references) → PR #3, squash-merged. #2 (A1's
    exhibit target) recorded as **blocked by #1** through the issue-dependencies API — the
    same mechanism the Seed Repo backlog uses, which means A1 item 6's second question now
    has a real answer in this repo's own data.
  - **The course repo now closes its own issues the way M06 teaches.** PR #3 merged at
    `15:27:45`; issue #1 closed at `15:27:46`. A **one-second gap** — the same evidence as
    the `cli/cli#14404` two-second gap the lesson is built on, produced here by a `Closes`
    keyword rather than a human. Both timestamps are quoted in M06.
  - **M06 was over-claiming.** It said "each of its six units was filed as a spec issue,
    decomposed into tickets with explicit blocking edges, built on a branch, reviewed, and
    merged" — false, and trivially falsified by any student who ran `gh pr list`, on a page
    whose whole subject is not asserting what the artifacts fail to show. Rewritten to
    describe the history that actually exists, including the fact that the first commit is
    a squashed import that demonstrates nothing about process. Re-audit this claim as the
    history grows.
  - Both `gh` commands now printed in `assignments/a1.md` and M06 were **run as written**
    against the live repo before shipping, not composed from memory.
  - Filed #4: `CONTEXT.md`'s Work Dependency entry repeats the sub-issue/dependency
    conflation already corrected in `seed/SPEC.md` §6. Kept out of PR #3 deliberately —
    scope-creeping an unrelated fix into a PR is the anti-pattern Week 4 teaches against,
    and this repo is an exhibit. **Closed by PR #6** later the same day: rather than
    deleting the wrong mention, `CONTEXT.md` now carries a term for each feature, because
    the difference is what M11 assesses. Carried through to Course Home's Week 2 blurb and
    to M11's own objective text, which previously cited only the sub-issues doc;
    `RESOURCES.md` gained the issue-dependencies REST page (URL checked, HTTP 200).
  - Both throwaway repos from the Seed Repo smoke test were deleted by hand; the org now
    holds `flashcards-seed` and `gh-pr-mastery` only.
- **2026-09-12** — `roadmap/roadmap.docx` added, generated by `roadmap/build_roadmap.py`
  on the same rule as the objectives workbook: the item list lives in the script and the
  document is disposable. 21 items across five sections — done, next, infrastructure,
  decisions owed, and pre-cohort operations. It deliberately does **not** restate the
  facts, sources, or open-question reasoning kept here; it links back instead, so the two
  cannot drift into contradicting each other. If a roadmap item and this file disagree,
  this file is right.
