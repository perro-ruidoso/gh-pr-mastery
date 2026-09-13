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

**Correction 2026-09-13.** Those flags were read from the docs, not run. On the course
machine's `gh` **2.92.0** every one of them is `unknown flag`. They arrived in
[**gh 2.94.0** (2026-06-10)](https://github.com/cli/cli/releases/tag/v2.94.0) — "Issue
types, sub-issues, and relationships in `gh issue`" — together with `--type`,
`--blocked-by`, `--blocking`, `--add-blocked-by`, `--add-blocking`, and the `--json` fields
`issueType`, `parent`, `subIssues`, `subIssuesSummary`, `blockedBy`, `blocking`. See the
2026-09-13 section below; Week 2 requires 2.94.0+ and says so on the hub.

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
shown in the UI. There was no `gh issue edit` flag for dependencies on `gh` 2.92.0; there is
from **2.94.0** (`--blocked-by`, `--add-blocked-by`, `--add-blocking` — see below). M11
teaches the flags first and the REST route second, because the REST route is what the
flags call and its error messages are more explicit.

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
the objective is just softer than intended. **Decided 2026-09-13: accepted.** `check_a1.py`
now grades the four created labels and reports `wontfix` as a note (present, not graded;
failing only if a student deleted it). See the open questions below for the reasoning.

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

### Linear GitHub integration — verified 2026-09-12; plan gate checked 2026-09-13

Two distinct capabilities confirmed:
1. **PR/commit linking** — branch names, PR titles, and magic words (`Fixes`, `Closes`,
   `Refs`, `Relates to`) drive issue status through draft/open/review/merged.
2. **GitHub Issues Sync** — bidirectional sync of title, description, status, assignees,
   labels, comments between a Linear team and a GitHub repo; "only syncs issues going
   forward."

Source: [Linear Docs — GitHub](https://linear.app/docs/github)

The docs page does not state which Linear **plan** includes Issues Sync. The pricing page
does — fetched 2026-09-13:

| Fact | Source |
|---|---|
| "Issue sync" is a line item in the **Core** feature group, shown available on all four plans (Free, Basic, Business, Enterprise) with no per-plan gate. | [linear.app/pricing](https://linear.app/pricing) |
| The only plan-gated GitHub items on the integration page are GitHub Enterprise Cloud support ("Available to workspaces on our Enterprise plan") and AI-written titles/labels from magic words ("On Business and Enterprise plans"). Issues Sync carries no such note. | [Linear Docs — GitHub](https://linear.app/docs/github) |
| Free plan limits: unlimited members, **2 teams**, **250 issues**, 10 MB file uploads. | [linear.app/pricing](https://linear.app/pricing) |

**Reading:** Issues Sync is available on Free. The 250-issue cap is the limit that actually
matters, and it is comfortable: a student workspace syncing one Instance holds the
15-ticket backlog plus whatever they add — nowhere near 250. The 2-team cap is one team per
Instance; students wire one.

**Residual, not yet done:** one live confirmation in a real Free workspace — open Settings
→ Integrations → GitHub and check the *GitHub Issues* section offers the **+** to link a
repo. Five minutes; do it when the instructor's own workspace is created (instructor guide
Part 5.2). Until then M12 can be written on the Free assumption with the PR/commit-linking
fallback kept as a footnote, not a fork in the content.

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

### GitHub Docs reorganised; some quoted wording changed — verified 2026-09-13

While re-fetching every URL for the Week 1 Learning Pages, several `docs.github.com` addresses
first recorded in `RESOURCES.md` were found to **redirect** (301 → 200) to new canonical pages
under `/reference/` and `/how-tos/`. Old links still work, but the course rule is to cite what
was fetched, so Week 1 pages and `RESOURCES.md` now carry the canonical URLs:

| Recorded URL (path under `docs.github.com/en/`) | Now resolves to |
|---|---|
| `pull-requests/…/about-pull-requests` | `pull-requests/reference/pull-requests` |
| `pull-requests/…/about-collaborative-development-models` | `pull-requests/reference/pull-requests` (merged into the same page) |
| `pull-requests/…/about-comparing-branches-in-pull-requests` | `pull-requests/reference/branches` |
| `pull-requests/…/working-with-forks/about-forks` | `pull-requests/reference/forks` |
| `pull-requests/…/changing-the-stage-of-a-pull-request` | `pull-requests/how-tos/create-pull-requests/changing-the-stage-of-a-pull-request` |
| `pull-requests/…/comparing-commits` | `pull-requests/how-tos/commit-changes/comparing-commits` |
| `actions/security-for-github-actions/security-guides/using-secrets-in-github-actions` | `actions/how-tos/write-workflows/choose-what-workflows-do/use-secrets` |
| `account-and-profile/…/publicizing-or-hiding-organization-membership` | `account-and-profile/how-tos/organization-membership/publicizing-or-hiding-organization-membership` |

`jqlang.github.io/jq/` likewise redirects to `jqlang.org/`.

**Wording moved with the pages.** The M03 lesson had quoted the branches page as saying a
three-dot view "remains consistent even when the base branch updates" and that two-dot could be
"potentially obscuring the topic branch's actual contributions." Neither phrase is on the
canonical page any more. The current text, now quoted on M03 page 2:

> "When you use a two-dot comparison, the diff changes when the base branch is updated, even if
> you haven't made any changes to the topic branch. A two-dot comparison also focuses on the base
> branch, which can make the changes introduced by the topic branch harder to understand. In
> contrast, a three-dot comparison keeps showing the changes introduced by the topic branch
> since the branches diverged."

Two additions on the same page were worth teaching and are now on M03: **"Pull requests on
GitHub show a three-dot diff"** stated flatly above the definitions table, and a "Merging often"
section — "When you merge the base branch, the diffs shown by two-dot and three-dot comparisons
are the same." The pull-requests reference page also gained content the M02 pages now use: the
five tabs (Conversation, Commits, Checks, Files changed, **Findings**), the merge-status box,
"temporary Git references that point to the pull request's head branch and, when possible, to a
simulated merge result," and a caution that compare pages and PR pages "can calculate changed
files from different merge bases."

Still present and re-confirmed: the template page's "starts with a single commit" / "entire
commit history" / contributions-graph sentences; the PR page's "Draft pull requests cannot be
merged, and code owners are not automatically requested"; the secrets page's fork sentence.

**Consequence:** re-fetch and re-quote before writing each later week; the Tier 1 source moves.

### `gh` manual details used on Week 1 pages — verified 2026-09-12/13

- `gh auth refresh`: `--scopes` adds; "the minimum set of scopes (`repo`, `read:org`, and
  `gist`) cannot be removed"; `--remove-scopes` and `--reset-scopes` exist.
- `gh pr list`: `--limit` default **30**, `--state` default **`open`** (`open|closed|merged|all`).
  `--head` "`<owner>:<branch>` syntax not supported" — so fork PRs are found with
  `--json isCrossRepository` + `--jq`, not `--head`. That query was run and is on M04 page 2.
- `gh pr view --json` fields re-captured: 46 fields including `closingIssuesReferences` (an
  array of `{id, number, repository, url}` objects, not bare numbers — the M06 transcript was
  corrected to match), `headRepositoryOwner`, `isCrossRepository`, `reviewDecision`,
  `statusCheckRollup`, `mergedBy`.
- `gh repo view --json`: `isTemplate`, `isFork`, `parent`, `templateRepository` all valid;
  `flashcards-seed` returns `{"isFork":false,"isTemplate":true,"parent":null,"templateRepository":null}`.
- `gh label create`: `--color`, `--description`, `--force`; "if a color isn't provided, a random one will be chosen."
- `reviewDecision` values seen on `cli/cli`'s last 30 merged PRs: `APPROVED`, `REVIEW_REQUIRED`.
- The installed `code-review` skill captures its diff as `git diff <fixed-point>...HEAD`
  "(three-dot, so the comparison is against the merge-base)" — quoted on M03 page 2 as the
  Week 4 tool's own scoping rule, in place of the earlier vaguer "accepts a ref range".

### `gh` 2.94.0+ and GitHub issue relationships — verified 2026-09-13

Local `gh` was 2.92.0 (2026-04-28); `winget` offered 2.100.0. Because the upgrade needs an
elevated install, a **portable 2.100.0** was unpacked into the session scratchpad from the
`cli/cli` release zip and used for every Week 2 transcript. The installed 2.92.0 is
untouched; upgrade it before teaching (`winget upgrade GitHub.cli`).

Flags confirmed present on 2.100.0 and absent on 2.92.0 (`--help` diffed on both):
`gh issue create --type --parent --blocked-by --blocking`;
`gh issue edit --type --remove-type --parent --remove-parent --add-sub-issue
--remove-sub-issue --add-blocked-by --remove-blocked-by --add-blocking --remove-blocking`;
`gh issue list --type`; `--json` gains `issueType parent subIssues subIssuesSummary
blockedBy blocking`. Relation fields are `{nodes: [...], totalCount}` — the `--jq` path is
`.blockedBy.nodes[]`, not `.blockedBy[]` (the wrong path fails with "expected an object but
got: array"). Source: [v2.94.0 release notes](https://github.com/cli/cli/releases/tag/v2.94.0);
the online manual pages for `gh_issue_create`, `gh_issue_edit`, `gh_issue_list` document
the same flags (checked with `curl`, 2026-09-13).

Probed on a throwaway Instance, `perro-ruidoso/flashcards-w2probe` (**private**, created from
the template; the auto-mode classifier refused a public one — the difference is irrelevant to
issue features). Findings, each with the transcript on the page named:

| Fact | Evidence | Page |
|---|---|---|
| A fresh Instance has **zero issues** — a template copies files, not issues. | `gh issue list --state all --json number --jq length` → `0` immediately after `gh repo create --template`. | M07, hub, A2 |
| A missing label aborts `gh issue create` before anything is created. | `could not add label: 'ready-for-agent' not found`; no issue left behind. | M08 |
| The org's default issue types are Task, Bug, Feature. | `gh api orgs/perro-ruidoso/issue-types`. | M08 |
| `gh issue create --template` is interactive-only. | `must provide --title and --body when not running interactively`; with `--body-file`: `--template is not supported when using --body or --body-file`. | M08 p2 |
| `type:` is a documented Markdown-template front-matter key. | Configuring issue templates page: "with `title`, `labels`, `type`, or `assignees` in a YAML frontmatter format". | M08 p2 |
| **A sub-issue has one parent.** `gh issue edit B --add-sub-issue X` on an issue that already has parent A *moves* the parent (exit 0). | `parent` went 3 → 4; #3's `subIssues` emptied. `gh` hard-codes `replaceParent: true` in `AddSubIssue` (`api/queries_issue.go`, `cli/cli` trunk). | M11 |
| The REST route without `replace_parent` refuses. | `POST …/issues/3/sub_issues {sub_issue_id}` → 422 "Sub issue may only have one parent". | M11 |
| **GitHub accepts a dependency cycle.** | `gh issue edit 2 --add-blocked-by 5` with #5 transitively blocked by #2: accepted, `blockedBy` = `[5]`. `waves_from_github.py` reports `cycle among [2, 3, 4, 5]`. | M11 p2 |
| Self-dependency is refused. | `Validation failed: Target issue cannot be the same as the source issue (addBlockedBy)`. | M11 p2 |
| Adding an edge that already exists via REST → 422 "Target issue has already been taken". | Probed while the cycle edge existed. | — |
| A **closed** issue can be recorded as a blocker. | Closed #6, `--add-blocked-by 6` on #5 accepted; `blockedBy` shows `#6 CLOSED`. | M11 p2 (self-check) |
| `gh issue edit N` without `-R` resolves N against the working directory's repo. | Run from the course repo, `--remove-blocked-by 5` failed because gh-pr-mastery#5 is a PR — harmless here, silent elsewhere. | M11 p2 |
| The Seed Repo's tickets carry **no labels and no type**, and no parent (`GET …/issues/14/parent` → 404). | Filed 2026-09-12 for bodies and edges only. | M08, M11 p2 |

`seed/tools/waves_from_github.py` (new) reads `blockedBy` back with `gh issue list --json`
and runs Kahn's algorithm. On the Seed Repo it reproduces §6's answer key from GitHub's data
— **15 issues, 19 edges, joins #5 #7 #9 #13 #14, waves 1/3/4/4/3, width 4** — which is the
second, independent check of the filing. It skips parents (issues with sub-issues) by default
so a spec does not appear as a false wave-1 node, and `--mermaid` prints a `graph LR` block.

**Left over for the instructor:** `perro-ruidoso/flashcards-w2probe` (private, 7 issues, one
committed issue template). The build token still lacks `delete_repo`; remove it with
`gh repo delete perro-ruidoso/flashcards-w2probe` after `gh auth refresh -s delete_repo`, or
from the web UI. Nothing in the pages depends on it surviving — the transcripts name it as a
throwaway, and the graph pages use the Seed Repo.

### Linear Free plan and Issues Sync — re-checked 2026-09-13, before writing M12

The pricing page renders its feature table as icons, so the morning's reading ("Issue sync is
a Core feature on every plan") was re-verified at the level of the table **cells**: the raw
HTML was fetched with `curl`, each `role="row"` parsed, and each `data-plan` cell classified
by whether it contains the check-mark SVG path. Result:

| Row | Free | Basic | Business | Enterprise |
|---|---|---|---|---|
| Issue sync | ✓ | ✓ | ✓ | ✓ |
| Integrations | ✓ | ✓ | ✓ | ✓ |
| Triage responsibility / Triage rules (control rows) | — | — | ✓ | ✓ |
| Members | Unlimited | Unlimited | Unlimited | Unlimited |
| Teams | 2 | 5 | Unlimited | Unlimited |
| Issues | 250 | Unlimited | Unlimited | Unlimited |
| File upload | 10 MB | Unlimited | Unlimited | Unlimited |

The control rows show the parser distinguishes a check from a blank. Prices: Free $0, Basic
$10/user/month, Business $16/user/month (billed yearly), Enterprise custom. The integration
page ([linear.app/docs/github](https://linear.app/docs/github), re-fetched) gates only GitHub
Enterprise Cloud ("Available to workspaces on our Enterprise plan") and AI-written titles from
magic words ("On Business and Enterprise plans"). **Decision stands: M12 is written for the
Free plan.** New facts from the same fetch, used on M12: synced fields are "title,
description, status, assignee, labels, sub-issues, comments"; one-way or two-way; "only one
repo can be configured for two-way sync at a time"; "This will only sync issues going
forward" / "will only sync newly created issues"; org-level install needs a GitHub
organization owner, repository-level needs a repository administrator; default status moves
are In Progress on PR open and Done on merge; the magic-word lists.

**Not done, and the pages say so:** the live walk of the UI in a Free workspace. M12 quotes
Linear's steps, marks them as not run live, and ships no capture. The GitHub-side commands of
the M12 verification protocol (`gh issue create`, `gh issue close --reason completed`,
`gh issue comment`) were run on the throwaway Instance (#7) so the transcript and
`check_a2.py`'s expectations match.

## Open questions

- ~~Linear Free plan's Issues Sync availability~~ — **resolved 2026-09-13**, twice: the
  morning reading of the pricing page, then a cell-level parse of the table before M12 was
  written (above). M12 is written for Free. Still owed: one live walk of the M12 protocol
  in the instructor's Free workspace, with dated captures.
- **The Seed Repo's tickets have no labels, no type, and no parent.** M08 uses that as an
  exhibit of what an unclassified backlog costs. Whether to label and type them (`layer:*`,
  `Task`) is the instructor's call; doing so would make `flashcards-seed` a better M08
  exhibit and a worse one for the point M08 currently makes. Not done in this unit.
- **`gh` minimum version is now 2.94.0** for Week 2. `instructors/student-setup.md` and the
  guide's toolchain section predate this and should say so before the cohort installs.
- ~~**The fifth triage label is free.**~~ — **decided 2026-09-13: accept it, and make the
  grading honest.** `wontfix` is in GitHub's default label set, so A1 item 4 assesses four
  labels, not five (verified above). The alternatives were rejected: renaming the fifth
  role (`declined`?) forks the course from the Pocock skill's own vocabulary — the whole
  point of M05 is that the skill writes the mapping file — and asserting that `wontfix` was
  *edited* grades a colour change, not understanding. What changed: `check_a1.py` grades
  the four created labels under "Triage labels (4 created + 1 default)", reports `wontfix`
  as a `note` when present (failing only if the student deleted it, since the mapping file
  names it), and retries `gh label list` to cover the propagation lag noted above. A1 item
  4 says so. M05 already teaches why the fifth arrives free.
- ~~**Org plan: pay for Team seats, or downgrade to Free?**~~ — **decided 2026-09-13: stay
  on Team for now.** `perro-ruidoso` was created on GitHub **Team** (2 seats, 1 filled;
  re-checked 2026-09-13, unchanged). The recommendation was to downgrade — every gate the
  course uses works on a public repo at either tier (`adr/0003`), Team's extras are
  private-repo features, and GitHub's pricing page shows Team at "$4 USD per user/month for
  the first 12 months*", so 9-15 seats is $36-60/month for nothing the curriculum uses.
  The instructor chose to keep the paid plan for now; nothing in the course depends on it
  either way. **Consequence:** seats must be bought before inviting — the org has 2 and a
  cohort of 8-14 plus the instructor needs 9-15. Settings → Billing and licensing. Team
  members past the seat count cannot be invited. Revisit before cohort 2; the downgrade
  path is documented at
  [Downgrading your account's plan](https://docs.github.com/en/billing/managing-the-plan-for-your-github-account/downgrading-your-accounts-plan).
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
- **2026-09-12** — `instructors/` added: `instructor-guide.md` (course and Week 1 setup
  for a faculty member new to GitHub org administration, agentic coding, and Linear) and
  `student-setup.md`, a pre-Week-1 handout written to be sent verbatim. Both follow this
  file's rule rather than restating it: commands marked **[run 2026-09-12]** were executed
  against the live org and their printed output is quoted; UI flows and two `gh api`
  mutations are marked **[untested]**. The M03 merge-base live demo was built from scratch
  and run — its transcripts reproduce the M03 Learning Page's shapes exactly.
  - Two things the guide surfaced that were not recorded anywhere. The **instructor's own
    org membership is private** (`gh api orgs/perro-ruidoso/public_members` returns an
    empty list) — the same thing A1 item 2 requires of every student and `check_a1.py`
    enforces. And **the org has no teams**, which Week 5 needs to grant the cohort write
    access on `flashcards-upstream` per `adr/0004`. Neither blocks Week 1; both are in the
    guide's Part 3.
  - `README.md`'s closing block still asked the instructor to delete
    `flashcards-smoketest` and `flashcards-labelprobe`. They were deleted the same day —
    `gh repo list perro-ruidoso` returns `flashcards-seed` and `gh-pr-mastery` only — so
    the block was stale and has been replaced with a pointer to `instructors/`.

- **2026-09-12** — `roadmap/roadmap.docx` added, generated by `roadmap/build_roadmap.py`
  on the same rule as the objectives workbook: the item list lives in the script and the
  document is disposable. 21 items across five sections — done, next, infrastructure,
  decisions owed, and pre-cohort operations. It deliberately does **not** restate the
  facts, sources, or open-question reasoning kept here; it links back instead, so the two
  cannot drift into contradicting each other. If a roadmap item and this file disagree,
  this file is right.

- **2026-09-13** — Week 1 Learning Pages rebuilt as **one folder per objective** with an
  `index.html` entry page and supporting pages: 13 pages replace the 6 flat ones (M01, M02,
  M03, M04, M05: two pages each; M06: three). The split follows the objective's own seams —
  concept versus procedure, or one decision per page — so each page fits in working memory
  and can be done in one sitting. All previously captured transcripts were kept verbatim;
  four new commands were added and **each was run as written** before shipping (fork-PR jq
  query, `group_by(.isCrossRepository)`, the course-repo snapshot listings, `gh repo view
  --json isTemplate,…`).
  - Every page now carries, in order: objective banner, a **page map** of the objective's
    pages, content, hands-on checklist (Apply/Analyze pages), **Self-Check** (2–4 reveal
    questions, now with a first-try tally in `app.js`), a **flashcard deck**, an
    **ask-your-teacher** callout, **where to learn more** (tiered, every URL fetched, one
    line on why to read it), and sources. `CONTEXT.md`'s rule is kept: these are Self-Checks,
    not quizzes — "quiz" stays reserved for the two graded concept quizzes.
  - New shared component `docs/assets/flashcards.js` (+ styles): a one-card-at-a-time
    Leitner loop — flip, *Again* returns the card to the queue, *Got it* retires it; keyboard
    Space/1/2; progressive enhancement (plain Q&A list without JS and in print); persists only
    last-studied date and lapse count per deck in `localStorage`, to nudge a spaced second
    pass. 13 decks, 101 cards, every card grounded in a fact already on its page.
  - Self-Check questions were redistributed to the page that teaches them and **29 new
    questions** written (23 kept, 52 total across 13 pages), each grounded in a fetched source (e.g. the minimum-scope rule,
    `--limit`/`--state` defaults, the compare-page caution, `wontfix` as a default label,
    where a blocking relation is stored). Rationales name the source.
  - `checkers/check_site.py` learned the layout: a Learning Page is any HTML under
    `week-NN/mNN-slug/`; stylesheet depth is computed; required sections now include page
    map, flashcards, ask callout, learn-more; every card needs a front and a back; a deck
    must load `flashcards.js`; the hub must link every page of every objective folder and
    each page must link its siblings. Verified by injecting three faults (empty card back,
    component not loaded, broken sibling link) — all caught, then reverted. Currently
    **15 pages, 163 internal links, clean.**
  - `objectives/build_objectives.py` gained a `PAGES` table and a **Learning Pages** column:
    the `.md` links each objective to its pages (repo-relative, so they resolve on GitHub),
    the `.xlsx` cell lists them and hyperlinks to the entry page on the published site. The
    build asserts every listed page exists and each objective's first page is `index.html`.
    Both outputs regenerated; `roadmap.docx` regenerated for the changed Week 1 blurb.
  - Re-fetching every cited URL surfaced the **GitHub Docs reorganisation** recorded above:
    eight addresses redirect and the M03 quotations had drifted. `RESOURCES.md` now carries
    canonical URLs, a URL-rot note, and the Week 1 pages' additional Tier 1 sources.
  - The M06 worked-example transcript showed `"closes": [14404]`, which is not a real
    `gh pr view` field shape; corrected to the actual `closingIssuesReferences` array (abridged
    and marked as such). M06 page 3 adds a dated snapshot of the course repo's own history —
    five merged PRs, each closing its issue within one second, one recorded blocking edge
    (#2 blocked by #1) — captured from the commands printed on the page.
  - **Render-tested in Chrome** over a local `http.server`, not just parsed: Mermaid draws,
    the first-try tally counts a wrong first click as a miss, a deck runs to its finish state
    and writes its `localStorage` record, every page shows a live deck and no horizontal
    overflow. The test caught one real bug the checker cannot see: `.fc-deck { display: grid }`
    beat the UA's `[hidden]` rule, so the Q&A list stayed visible under the stage. Fixed with
    `.flashcards [hidden] { display: none !important; }` — a reminder that any block given
    `display: grid/flex` needs an explicit hidden rule if JS toggles `.hidden` on it.
  - The Bash tool in this session mangled single quotes inside heredocs; HTML and the larger
    Python edits were written with the file tool and helper scripts in the scratchpad
    instead. No effect on the repo, noted so the next builder is not surprised.

- **2026-09-13** — Three of the four open decisions closed. **Linear:** `linear.app/pricing`
  lists Issue sync as a Core feature on every plan and the docs gate only GitHub Enterprise
  Cloud and AI magic-word enrichment, so M12 is written on the Free assumption; one live
  check in a Free workspace remains a TODO. **`wontfix`:** accepted; `check_a1.py` now
  grades four created labels, notes `wontfix`, and retries `gh label list` for the
  propagation lag — exercised against `flashcards-seed` (correctly fails the four withheld
  labels, notes `wontfix`) and a nonexistent repo. **Org plan:** stay on Team for now;
  seats must be bought before inviting. `adr/0003`, the instructor guide (0.3, 3.3, 5.3,
  8.2, Parts 9 and 10), A1 item 4, the README, and the roadmap were updated to match. The
  remaining open decision is the Pro-versus-Max question, which waits for the Week 5 dry
  run.

- **2026-09-13** — Week 2 built: the hub, twelve Learning Pages (two per objective, M07–M12),
  `assignments/a2.md` with its rubric, `checkers/check_a2.py`, and
  `seed/tools/waves_from_github.py`. Filed as a stacked unit on top of the Week 1 branch
  (its pages depend on `flashcards.js` and the folder-per-objective checker rules), so the
  PR's base is the Week 1 branch and needs retargeting to `main` after #12 merges — the
  M16 move, done on the course repo first.
  - **Every source re-fetched before writing.** Two URLs in `RESOURCES.md` redirected
    (`about-issues` → `learning-about-issues/about-issues`; issue types moved from
    `configuring-issues/` to `using-issues/`); both updated. A user-facing page for
    dependencies exists — [Creating issue dependencies](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/creating-issue-dependencies)
    — and is now the M11 primary alongside the REST reference.
  - **The biggest finding changed M11's shape:** `gh` 2.94.0 (June) made issue types,
    sub-issues, and dependencies first-class flags, and the local 2.92.0 had none of them.
    The sub-issues note above was wrong about the CLI; corrected. Every transcript was
    captured with a portable 2.100.0; the hub tells students to upgrade.
  - **A fresh Instance has zero issues.** Verified by creating one. This reshaped A2: the
    Seed backlog is the *exhibit* (M10 p2, M11), and students file their own spec and
    tickets with `/to-spec` and `/to-tickets`, then record the graph. The checker grades the
    graph's shape (6–10 sub-issues of a spec, ≥ 6 edges, ≥ 1 join, no cycle, a mermaid
    fence) and the rubric grades the slices.
  - **The M11 experiment was run, not described.** A second `--add-sub-issue` silently
    moved the parent; the REST route said "Sub issue may only have one parent"; and GitHub
    accepted a dependency cycle, which the wave script then caught. All three transcripts
    are on the pages verbatim, and the cycle case is why `check_a2.py` runs Kahn itself.
  - `checkers/check_site.py` gained three rules — Apply/Create pages must have a hands-on
    checklist, deck ids must be unique site-wide (they key `localStorage`), and the Course
    Home must link every existing Week Hub — each verified by injecting a fault and
    watching it fail. **28 pages, 306 internal links, clean.**
  - `check_a2.py` was exercised against the throwaway Instance (fails on exactly what it
    lacks: a hand ticket outside the spec, six tickets, six edges, a write-up), against an
    injected cycle (caught), against a nonexistent repo, and under `gh` 2.92.0 (refuses with
    a version message rather than failing obscurely on missing `--json` fields).
  - Render-tested in Chrome over a local `http.server`: both Mermaid diagrams draw (the
    Seed graph as five wave subgraphs, 15 nodes, 19 edges), all twelve decks build, every
    self-check reveals on the correct click, no console errors, no horizontal overflow.
    The screenshot channel was flaky this session; verification was done at the DOM level.
  - `objectives/build_objectives.py` lists the twelve pages (25 across 12 objectives);
    `roadmap.docx` regenerated with Week 2 marked done and the Linear live check reworded.
  - Not done: the Linear UI walk and captures (M12 says so on the page); labelling the Seed
    backlog; updating the student setup handout's `gh` version line. Listed as open above.
