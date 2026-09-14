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
`cli/cli` release zip and used for every Week 2 transcript. *(Superseded later the same day:
the `winget upgrade GitHub.cli` completed after its UAC prompt, and the installed `gh` is
now **2.100.0 (2026-09-03)** — the Week 1–2 audit below ran on it.)*

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

**Left over for the instructor:** `perro-ruidoso/flashcards-w2probe` (private, 8 issues after
the audit's fault-injection — #8 closed as not planned — one committed issue template). The
build token still lacks `delete_repo` (re-checked 2026-09-13); remove it with
`gh repo delete perro-ruidoso/flashcards-w2probe` after `gh auth refresh -s delete_repo`, or
from the web UI. Nothing in the pages depends on it surviving — the transcripts name it as a
throwaway, and the graph pages use the Seed Repo.

### A stacked PR's closing keyword is ignored until it targets the default branch — verified 2026-09-13

Found by dogfooding this unit. PR #14 (Week 2) was opened with base
`11-week1-pages-flashcards-learn-more` (the Week 1 branch, PR #12) and `Closes #13` in its
body; `gh pr view 14 --json closingIssuesReferences` returned `[]`. GitHub's linking page,
re-fetched: "If the pull request targets *any other branch*, then these keywords are ignored,
no links are created, and merging the PR has no effect on the issues." So a stacked PR does
not link its issue until it is retargeted to `main` after its parent merges — at which point
the keyword takes effect and `closingIssuesReferences` populates. This is the M15/M16
interaction Week 3 must teach: **retarget, then re-check the link.** Until then, #13's
relation to #14 is visible only in the PR body and the branch name.

Source: [Linking a pull request to an issue](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/linking-a-pull-request-to-an-issue)

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

### Week 1–2 audit — 2026-09-13

Hostile re-check of everything shipped for Weeks 1 and 2, run with the tools live rather
than from memory. Precondition: the installed `gh` is now **2.100.0 (2026-09-03)** — the
`winget upgrade GitHub.cli` started earlier in the day completed in the background, so
the "portable build" workaround above is history and every command in this audit ran on
the installed binary. Filed as issue #15; the work is on branch `15-audit-weeks-1-2`.
Each row: **fact · evidence · page · fixed or open.**

#### 1. Sources — every URL re-fetched

90 distinct external URLs across `RESOURCES.md`, the two Week Hubs, and all 25 Week 1–2
Learning Pages were fetched with `curl -sL` and their final status, redirect count, and
effective URL recorded. Every quotation on every page (any `"…"` span of four words or more
outside `<pre>`) was then searched for, on an alphanumeric-only comparison, in the fetched
text of the sources that page cites, and the survivors were read by hand.

| Fact | Evidence | Page | Status |
|---|---|---|---|
| Three `RESOURCES.md` rows for Weeks 3–5 had moved: *Changing the base branch* → `pull-requests/how-tos/create-pull-requests/…`; *Reviewing proposed changes* → `pull-requests/how-tos/review-pull-requests/…`; *About continuous integration* → `actions/get-started/continuous-integration`. | `curl -sL -w '%{http_code} %{url_effective} %{num_redirects}'`: 200 via one 301 each. | `RESOURCES.md` (M16, M19/M20, M25 rows) | **Fixed** — canonical URLs, dated. |
| No other URL redirected or failed. Every `docs.github.com`, `cli.github.com`, `code.claude.com`, `git-scm.com`, `jqlang.org`, `mermaid.js.org`, `linear.app`, and `github.com` link answered 200 with zero redirects. | Same fetch; 87 rows `200 0`. | all | Verified. |
| Three `github.com/perro-ruidoso/flashcards-w2probe/issues/N` URLs return **404** to anyone but the instructor. | The Instance is private. | M11 p1, M11 p2 | Not a defect — they are the `gh` output printed in transcripts, not hyperlinks, and the pages call the repo a throwaway. Unchanged. |
| A quoted sentence on M11 p1 no longer exists: *"Sub-issues add support for hierarchies of issues on GitHub by creating relationships between your issues."* | Not on the fetched *Adding sub-issues* page; the current sentence is *"Your sub-issues can themselves contain sub-issues, allowing you to create full hierarchies of issues that visualize entire projects or pieces of work and show the relationships between your issues."* | M11 p1 | **Fixed** — re-quoted. |
| M06 p3's source line quoted *"up to eight levels of nesting"*; the page says *"create up to eight levels of nested sub-issues."* | Fetched text. | M06 p3 (sources) | **Fixed** — quoted as written. |
| M12 quotes Linear's synced-property list as one comma-separated string. | On the fetched page it is a bulleted list (`title` / `description` / `status` / `assignee` / `labels` / `sub-issues` / `comments`); each word is verbatim. | M12 p1, p2 | Left as is; noted here so nobody "corrects" it into a sentence Linear did not write. |
| Every other quotation checked — the M02 PR definitions, the M03 two-dot/three-dot and compare-page cautions (now on the *Pull requests* reference page, not *Branches*), the M01 template and scope sentences, the M05/M07/M09/M10 skill quotes (checked against the installed `SKILL.md` files under `~/.agents/skills/`), the M08 template-frontmatter sentence, the M11 REST `issue_id` description and the `+ icon` sentence on M12 — is present verbatim on its source. | `qcheck.py` in the session scratchpad + hand reading of the ~120 spans it could not match (all of them prompts, transcript strings, or the course's own prose in quotation marks). | all | Verified. |

#### 2. Transcripts — every printed `gh` command re-run

Every command printed on a Week 1–2 page against `cli/cli`, `perro-ruidoso/gh-pr-mastery`,
or `perro-ruidoso/flashcards-seed` was run again on `gh` 2.100.0 and diffed against the page.

| Fact | Evidence | Page | Status |
|---|---|---|---|
| **`cli/cli#14398`, the M02/M04 worked example, was closed unmerged on 2026-09-13.** Every page called it "an actual open pull request" and printed `"state": "OPEN"`. | `gh pr view 14398 -R cli/cli --json state,closedAt,mergedAt` → `CLOSED`, `2026-09-13T06:06:03Z`, `null`. | M02 p1, M04 p1 | **Fixed** — transcripts re-captured with `"state": "CLOSED"` and the framing changed: the PR was open on 09-12, closed the next morning, and closing changed `state` and nothing else (the base/head sentence still reads the same). M04 p1 adds that `view` reads any state; `list`'s defaults are what hide closed PRs. |
| `gh pr list -R cli/cli --limit 3` no longer lists #14398; the live top three are #14373 (fork), #14355, #14351 (both drafts, same-repo). M02 p2's text said "two of these heads are written `owner:branch`" — now one is. | Live listing 2026-09-13. | M02 p2, M04 p1 | **Fixed** — listings re-captured, dated in the prose, and the fork/bare-branch count corrected. |
| `gh pr list --limit 1 --json number --jq '.[0].number'` prints `14373`, not `14398`; the self-check question quoted the old number. | Live. | M04 p2 | **Fixed** — transcript and question updated; the `gh pr diff --name-only` example now follows the same PR (`docs/install_linux.md`). |
| `gh issue list -R cli/cli --limit 3` — #14432 gained the `more-info-needed` label. | Live. | M04 p2 | **Fixed** (one label in a transcript; the prose about triage labels still holds). |
| `gh pr view 14398 --json nope` — the "Available fields" list is unchanged (46 fields). | Live. | M04 p1 | Verified. |
| `cli/cli#14404` / `#14429` — every field identical: `closedAt 15:55:42`, `mergedAt 15:55:40`, 63/4/3, `closingIssuesReferences` → 14404. | Live. | M06 p1 | Verified, dated on the page. |
| `gh api orgs/perro-ruidoso/issue-types` — Task / Bug / Feature, same descriptions. | Live. | M08 p1 | Verified. |
| `gh issue view 1 -R perro-ruidoso/flashcards-seed --json title,body` — identical except that the page's transcript is hard-wrapped at ~85 columns for display and the live body is not. | `difflib` on the two texts. | M07 p1 | Verified; wrapping only. |
| The Seed backlog listing (`--json number,title,blockedBy`) and `waves_from_github.py` output are byte-identical to the pages: **15 issues, 19 edges, joins #5 #7 #9 #13 #14, waves 1/3/4/4/3, width 4** — which is `seed/SPEC.md` §6's answer key under the T→# mapping (T04→#5, T06→#9, T08→#7, T10→#13, T13→#14). | Live run 2026-09-13. | M10 p2, M11 p2 | Verified — `waves_from_github.py` still reproduces §6. |
| `gh api …/flashcards-seed/issues/14/dependencies/blocked_by` → #11 (id 5434030684), #7 (id 5434030220). | Live. | M11 p2 | Verified. |
| The `perro-ruidoso/gh-pr-mastery` snapshots on M06 p3 were two PRs and one dependency edge behind. | See §3–4. | M06 p3 | **Fixed** (below). |
| Commands printed against `flashcards-w2probe` (M08 p2, M11) were not re-run: they are mutations on a throwaway, the pages call it a throwaway, and the repository is private. The two `gh` error strings they quote (`--template is not supported when using --body or --body-file`, `Sub issue may only have one parent`) were re-confirmed on 2.100.0 during the checker fault-injection in §5. | — | M08 p2, M11 p1 | Out of scope by design; noted. |

#### 3. The stacked PR — #14 retargeted, linked, and closing #13

All from `gh` on 2026-09-13:

```
$ gh pr view 14 -R perro-ruidoso/gh-pr-mastery --json baseRefName,createdAt,mergedAt,closingIssuesReferences
{"baseRefName":"main","closingIssuesReferences":[{"number":13,…}],
 "createdAt":"2026-09-13T15:06:47Z","mergedAt":"2026-09-13T15:43:30Z"}
$ gh api repos/perro-ruidoso/gh-pr-mastery/issues/14/timeline --jq '.[] | select(.event=="base_ref_changed" or .event=="merged") | "\(.created_at)  \(.event)"'
2026-09-13T15:40:05Z  base_ref_changed
2026-09-13T15:43:30Z  merged
$ gh issue view 13 -R perro-ruidoso/gh-pr-mastery --json state,closedAt,stateReason
{"closedAt":"2026-09-13T15:43:31Z","state":"CLOSED","stateReason":"COMPLETED"}
$ gh pr view 12 -R perro-ruidoso/gh-pr-mastery --json mergedAt ; gh issue view 11 … --json closedAt
2026-09-13T15:40:01Z ; 2026-09-13T15:40:03Z
```

So: PR #12 (parent) merged **15:40:01** and closed #11 at **15:40:03**; #14's base was changed
to `main` at **15:40:05**; #14 merged at **15:43:30** and closed #13 at **15:43:31**;
`closingIssuesReferences` on #14, empty while it targeted the Week 1 branch (recorded above
on the day), now lists **#13**. One more artifact the earlier note missed: **#13 is recorded
as blocked by #11** (`dependencies/blocked_by` → `#11 [closed]`, `blocked_by_added` event at
15:05:53). This is now the **second worked example on M06 p1**, with the three transcripts
above, an observation/inference table, and a diagram — because it demonstrates the M06
two-second gap, the M15 keyword rule, and the M16 retarget on a repository every student can
read.

#### 4. M06 over-claiming — re-read against the live history

| Claim on M06 p3 | True on 2026-09-13? | Status |
|---|---|---|
| "Five merged PRs; every one has a non-empty `closingIssuesReferences`" | No — seven (#3 #5 #6 #8 #10 #12 #14), all with references; plus one open issue (#15, this audit) with no PR yet. | **Fixed** — snapshot re-captured, count and population statement updated. |
| "Run the same command for the other issues and you will find they have no recorded blockers" | **False** since #13 was filed: `#13 blocked_by → #11`. | **Fixed** — the page now says exactly one more edge exists and names it. |
| Issue numbers "1, 2, 4, 7, 9 — and PR numbers 3, 5, 6, 8, 10" | Stale. | **Fixed** — 1 2 4 7 9 11 13 15 / 3 5 6 8 10 12 14 (page text and flashcard). |
| "reached through an API endpoint rather than a `gh issue` flag" and the self-check rationale "there is no `gh issue` flag for them yet" | **False** on the `gh` the course now requires: `gh issue view --json blockedBy` and `--add-blocked-by` exist from 2.94.0 (the page's own flashcard already said so). | **Fixed** — both sentences now say "the REST endpoint on any version; from 2.94.0 also `--json blockedBy`". |
| One-second gaps "every time" | Still true, and now includes a two-second one (#11). | Table extended with #12/#11 and #14/#13; wording "one- and two-second". |
| "whether a PR's base was `main` or another feature branch" (listed as something a student *might* notice) | Now a real case (#14). | Sentence extended to point at it. |
| The squashed-import paragraph, the branch-naming inference, the "exhibit not model answer" framing | Still true. | Unchanged. |

#### 5. Checkers — run, and fault-injected rule by rule

- `check_site.py`: **28 pages, 306 internal links, clean** before and after every change in
  this audit. Then 25 faults were injected into a scratch copy of `docs/` (one per rule:
  broken link, no title, wrong stylesheet depth, Mermaid used/not loaded and loaded/not used,
  each of the eight required lesson sections, Apply page without a checklist, deck
  component loaded/not loaded, empty card front, empty card back, deck without id,
  `data-answer` naming a missing option, duplicate deck id, Course Home missing a hub, hub
  missing a page, page map missing a sibling, objective folder without `index.html`).
  **23 of 25 were caught on the first run.** One miss was the harness's (it broke one of the two
  sibling links and the pager still carried the other; breaking both is caught). **The other was
  a real checker bug:**
  `CARD_FRONT = <div class="fc-front">\s*\S` is satisfied by the `<` of the closing tag, so
  an empty `<div class="fc-front"></div>` passed; the back-face check only caught its fault
  through a regex-boundary accident. Both patterns now read `(?!\s*</div>)\s*\S`. **25/25
  after the fix**, and the real tree still passes.
- `check_a1.py` against `flashcards-seed`: fails on exactly the student-produced items
  (three `docs/agents/*` files, the `## Agent skills` section, the four created labels,
  `a1-writeup.md`) plus the two that cannot hold for the template itself (created-from-
  template, and org membership of a user called `seed`). Against `flashcards-w2probe`:
  same student items fail; template and labels pass; `Public` fails because it is private.
- `check_a2.py` against `flashcards-seed`: every rule fails, as it should (no labels, no
  template, fifteen unlabelled untyped issues, no spec, no probe, no write-up). Against
  `flashcards-w2probe`: fails on exactly the four things it lacks (hand ticket, 6–10
  tickets, 6+ edges, write-up), as recorded on the day it was built.
- Fault injection on `flashcards-w2probe` (it exists, is private, and is a throwaway), one
  mutation per reachable rule, then reverted and re-run to the pre-injection output:
  ticket loses its type → *Every ticket typed Task* and *Every open issue has a type*;
  spec loses `ready-for-agent` and becomes a Task → both spec rules and *Every open issue
  has a label*; mermaid fence removed → caught; layer label removed → caught; cycle
  `#2 ← #5` → *Graph is a DAG: cycle among #2, #3, #4, #5*; join edge removed → *At least
  one two-parent join* and *Blocked-by lines are recorded edges* (`#5 cites [4] in prose
  only`); probe reopened → *closed with reason completed* (`state=OPEN reason=REOPENED`);
  probe comment deleted → *has a comment* (`0 comment(s)`); template rewritten without
  `type:`, with a heading missing and a `tests/` line → all three template rules; a hand
  ticket without a test path → *names a test file*; a five-word `a2-writeup.md` with no
  image → *length* and *references a capture*; `wontfix` deleted → `check_a1.py` *Label
  wontfix — deleted?*; a nonexistent handle → *Instance exists* on both checkers.
  **Every injected fault was reported by name.** Two rules were not reachable without
  building a second spec (*Probe created after the spec*) or a Linear-titled closed PR
  (*PR preview*, a note, not a check); both were exercised on the day they were written.

#### 6. Render — every page, in Chrome, at 1200 px and 400 px

Served `docs/` over `http.server` and drove each of the 28 pages from a harness in the page
(same-origin iframe at the target width; decks flipped and graded to their finish state;
every self-check clicked wrong-then-right). Results:

| Check | 1200 px | 400 px |
|---|---|---|
| Mermaid diagrams drawn (6 across 5 pages, including the new M06 one) | 6/6, no error text | 6/6 |
| Decks built and run to "Deck complete" with the list hidden and a `localStorage` record written (25 decks, 187 cards) | 25/25 | 25/25 |
| Self-checks: wrong first click marks `.incorrect` and leaves the rationale hidden; the correct click reveals it; tally reads `0 / N` after a wrong-first pass and `N / N` after a correct-first pass (93 questions) | 93/93 | 93/93 |
| Console errors / in-frame `error` events | none | none |
| Horizontal overflow (`scrollWidth > clientWidth`) | none | **7 pages overflowed** (M01 p2, M02 p1, M02 p2, M04 p1, M06 p1, M06 p3, M11 p1; worst 906 px on a 385 px viewport) |

**Cause and fix:** `.code-label` — the `$ gh …` line above each transcript — is a block with
normal wrapping, but a `--jq '{…}'` argument is one unbreakable token wider than a phone. It
had no `overflow-x` rule, so it widened the document. Added `overflow-wrap: anywhere` to
`.code-label` and to inline `code` outside `pre` (M01 p2 had a 391 px inline field list).
Re-run: **0 overflows at 400 px**, nothing else changed. Note for the next builder: the
harness result at 400 px was identical before and after the CSS edit on the first re-run
because the stylesheet was cached; fetch it with `cache: 'reload'` before trusting a re-test.

#### 7. Self-check quality — option form

Analysed every question for the three tells named in the brief: correct option uniquely the
longest, uniquely the shortest, or the only one carrying a `<code>` element. **81 of 93
questions were flagged**: 77 for "longest" — the classic tell — 4 for "shortest", and 10
for "only code" (some for two reasons). Every flagged question was rewritten: the correct option keeps its substance
and each distractor keeps its meaning (rationales refer to them by letter), but distractors
were lengthened or trimmed and given code elements where needed so that no option stands
out by form. Two questions with fixed vocabulary (the four PR tabs; the two development
models) were re-shaped with a short gloss per option. Second pass caught 29 over-corrections
(correct now uniquely shortest). **Final: 93 questions, 0 flagged;** correct letters
distribute 24/23/21/25 across A–D; `check_site.py` still clean.

#### 8. Cleanup

- `flashcards-w2probe`: **not deleted** — `gh auth status` shows `admin:org, gist, project,
  repo, workflow` and no `delete_repo`. Command for the instructor:
  `gh auth refresh -s delete_repo && gh repo delete perro-ruidoso/flashcards-w2probe --yes`.
  It was restored to its pre-injection state (§5) so the M08/M11/M12 transcripts still match
  it, though nothing on the pages depends on it surviving.
- `README.md` Status: added the audit paragraph; Week 2 was already described as built.
- `roadmap/build_roadmap.py`: course-repo item updated (seven PRs, two edges, one stacked
  PR); new DONE item for the audit; Week 2 item notes 2.100.0 is now installed; new TODO for
  deleting the probe. `roadmap.docx` regenerated (26 items).
- `instructors/instructor-guide.md`: Part 1's dependency paragraph and the reference-state
  line no longer say the teaching machine is on 2.92.0; 7.3 records #14398's closure; 7.4
  now walks seven PRs and #14's retarget; Part 10 items 3 and 5 record the audit and give
  the delete command. Appendix A's `gh pr view 14398` line notes the state.
- Week 1 page footers: "Source links verified 2026-09-13" (they were re-fetched today).
- The open question above about the `gh` minimum version and the setup handout is closed:
  `student-setup.md` already asks for 2.94.0+ and the teaching machine is at 2.100.0.

**Claims that turned out to be false** (the PR body repeats this list): `cli/cli#14398` is
open; two of three listed heads are fork heads; `--limit 1` prints 14398; the course repo
has five merged PRs; no course-repo issue other than #2 has a recorded blocker; there is no
`gh issue` flag for dependencies; the M11 sub-issues quotation; the "eight levels of
nesting" quotation; this file's and the guide's statement that the teaching machine is on
2.92.0 and needs a portable build (true when written, false now); `check_site.py` catches
an empty flashcard face.

### Week 3 — branches, stacked PRs, conflicts — verified 2026-09-13

Everything below was **run**, not read, on a second throwaway Instance,
`perro-ruidoso/flashcards-w3probe` (private, created from the template at 16:55 UTC), with
`gh` 2.100.0 and git 2.52.0. Three tickets were filed (#1 review state on `Card`; #2 persist it,
`--blocked-by 1`; #3 tag field, `--blocked-by 1`), then the week was done end to end: PRs #4–#7,
plus two probe pairs #8–#11. The transcripts on the Week 3 pages are these runs verbatim.

#### Sources — every URL fetched before writing

Every Week 3 row already in `RESOURCES.md` answered 200 with no redirect. Five URLs new to the
course redirected once each (301 → 200) and are recorded canonically: `addressing-merge-conflicts/
about-merge-conflicts` → `pull-requests/reference/merge-conflicts`; `…/resolving-a-merge-conflict-
using-the-command-line` and `…-on-github` → `pull-requests/how-tos/merge-and-close-pull-requests/…`;
`proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request` →
`how-tos/create-pull-requests/creating-a-pull-request`; `incorporating-changes-from-a-pull-request/
about-pull-request-merges` → `pull-requests/reference/pull-request-merges`. Two guessed URLs were
**404** and are not cited: `…/creating-a-pull-request-template` and `…/deleting-and-restoring-
branches-in-a-pull-request` (both old and `how-tos/` spellings). The Linear page, the Pocock repo
README, the Anthropic skills page, git-scm.com, and the Google eng-practices page all answered
200 with no redirect.

#### `gh issue develop` and linked branches

| Fact | Evidence | Page |
|---|---|---|
| The default branch name is `<number>-<whole title slugified>` — 68 characters for #1. `--name` replaces it. | `gh issue develop 1 --checkout` → `1-add-review-state-to-card-repetitions-ease-factor-interval-due-date`. | M13 p1 |
| The branch is created on GitHub first, from the default branch, then fetched; `--checkout` checks it out. | URL printed before the fetch lines; `git log -1` shows only the template's initial commit. | M13 p1 |
| The link is stored server-side and readable by GraphQL `issue.linkedBranches`. | Query returned the branch name. | M13 p1 |
| **`--list` goes empty the moment a PR is opened from the branch**, as the docs say ("the connection with that branch is removed and only the pull request is shown"). | `gh issue develop --list 1` → the branch; after `gh pr create`, nothing. | M13 p1 |
| `--base B` starts the branch at B's tip **and** writes `branch.<name>.gh-merge-base = B`; `gh pr create` with no `--base` then targets B. | `git config --get branch.2-persist-review-state.gh-merge-base` → #1's branch; PR #5 opened against it with no flag. | M13 p1, M16 p1 |
| One issue can have several linked branches; a second `gh issue develop 3 --name …` succeeded while #3 already had a branch with a (closed) PR. | #3: `3-tag-field-on-card` (PR #6) and `3-tag-field-on-card-clean` (PR #7). | M13 p1, M14 p2 |
| Linear links a PR from a branch name containing the Linear issue ID; GitHub links by the stored relation. **Linear half not run live** (no workspace); quoted from the docs. | linear.app/docs/github, "Branch name" and FAQ. | M13 p2 |

#### Closing keywords and `closingIssuesReferences`

| Fact | Evidence | Page |
|---|---|---|
| `closingIssuesReferences` is **empty in the second the PR is created** and populates a moment later; the issue gets a `connected` timeline event. | PR #4 created 17:00:19: `closes: []` at once, `[1]` at 17:00:34; issue #1 `connected` 17:00:21. | M15 p2 |
| The `closed` event on an issue closed by a PR-body keyword has `commit_id: null` (the docs say it is present when a *commit's* keyword closed it). | `…/issues/1/timeline`. | M15 p2 (learn more) |
| A keyword on a PR whose base is another feature branch creates **no link, however long you wait**; retargeting to `main` creates it within a second. | PR #5: `closes: []` at +20 s, still `[]` after the parent merged; `gh pr edit 5 --base main` at 17:03:12 → `closes: [2]`, issue #2 `connected` 17:03:13. | M15 p2, M16 p2 |
| Merge → issue closed as `COMPLETED` one second later, three times out of three. | #4/#1 17:02:47→48; #7/#3 17:09:14→15; #5/#2 17:12:47→48. | M15 p2 |
| `gh issue view --json closedByPullRequestsReferences` lists only open or merged PRs; a closed-unmerged PR drops out of it while `gh pr list --json closingIssuesReferences` still shows the link on the PR side. | #3 → `[7]`; PR #6 (closed) still `closes=[3]`. | M14 p2, M15 p2 |
| `gh pr diff` has no `--stat`. | `unknown flag: --stat` on 2.100.0; use `--name-only` or `gh pr view --json additions,deletions,changedFiles,files`. | M14 p1 |

#### Stacked PRs, retargeting, and the squash

| Fact | Evidence | Page |
|---|---|---|
| A stacked PR's diff shows only the child's work while its base is the parent branch. | PR #5: 3 files, +88 −6; `models.py` (changed by #1) absent. | M16 p1 |
| GitHub does not update a child when its parent merges (the docs' "does not update the base branch's commit"). | PR #5 five seconds after #4 merged: base unchanged, `closes: []`, 3 files. | M16 p2 |
| **After a squash-merged parent, retargeting makes the child's diff grow** to include the parent's changes — the merge base falls back to the initial commit — but it stays `MERGEABLE` (identical changes on both sides). | After `--base main`: 5 files, +151; `git merge-base origin/main HEAD` → `e474711`. | M16 p2 |
| `git rebase origin/main` drops the already-squashed commit by itself: "warning: skipped previously applied commit 58cab2d"; the diff returns to the child's files. | Merge base → `0b9a901`; PR #5 back to 3 files, 1 commit `37d4731`, after `--force-with-lease`. | M16 p2 |
| GraphQL `BaseRefChangedEvent` carries `previousRefName`/`currentRefName`; REST `base_ref_changed` carries only the time. | Both queried on PR #5 and on gh-pr-mastery #14. | M16 p2, `check_a3.py` |
| Course repo #12 → #14, complete: #12 squash-merged 15:40:01 (`cf6d380`), #11 closed 15:40:03, #14 base changed 15:40:05 (`11-week1-pages-flashcards-learn-more` → `main`), #14 head force-pushed 15:42:45 (`32ac8c2` → `3af3c05` — the rebase onto the squash), #14 squash-merged 15:43:30 (`e28ce3d`), #13 closed 15:43:31. **Issue #13 has no `connected` event at all**; the second `closingIssuesReferences` populated is not on record. | GraphQL timeline of #14; `gh pr view 12/14`; `gh issue view 11/13`; REST timeline of #13. | M16 p2, M15 p2 |
| **`gh pr merge --squash --delete-branch` on a parent CLOSES the stacked child**: `base_ref_deleted` one second after the merge, `closed` a second later, base unchanged, no retarget. The docs' sentence ("GitHub automatically updates any such pull requests, changing their base branch…") did not apply. | Probe 1: PR #8 merged 17:13:33; PR #9 `base_ref_deleted` 17:13:34, `closed` 17:13:35, actor the user. | M16 p3 |
| **The repository setting *Automatically delete head branches* + a plain merge RETARGETS the child**: `automatic_base_change_succeeded`, `oldBase` → `newBase`, two seconds after the merge, PR still open. | Probe 2: `delete_branch_on_merge=true`; PR #10 merged 17:15:51; PR #11 event 17:15:53. Setting restored to `false`, #11 closed. | M16 p3 |
| Not probed: deleting the branch from the web UI's *Delete branch* button, or `git push origin --delete`. | — | M16 p3 says so |

#### Conflicts and the skill

| Fact | Evidence | Page |
|---|---|---|
| Two frontier tickets with no edge between them (#2, #3) both touched `Card` — the docstring line after `due`, and the end of `tests/domain/test_models.py`. A genuine two-file conflict: #2's second commit added a `datetime` guard motivated by the file format; #3 added `tags`. | `git merge origin/main` → `CONFLICT (content)` ×2; `git status --short` → `UU` ×2, `CONTEXT.md` `M` (clean). | M17 p1 |
| `mergeable` goes **`UNKNOWN` before `CONFLICTING`**: 20 s after the sibling merged it was `UNKNOWN`/`UNKNOWN`; 35 s after, `CONFLICTING`/`DIRTY`. | `gh pr view 5 --json mergeable,mergeStateStatus` ×3. | M17 p1 |
| The `datetime` guard and `has_tag` landed in the same method without conflict — git's "non-overlapping … incorporated verbatim". | Combined diff, two `+` columns, no markers. | M17 p1 |
| `/resolving-merge-conflicts` was invoked in Claude Code with the merge stopped; each of its five steps was executed and captured: state (`git status`, `git log --graph HEAD MERGE_HEAD`, `--diff-filter=U`); sources (commit `3b9501a`'s body, PR #7's body, issue #3's criteria); resolution keeping both sides (markers 0, nothing invented); checks (`pytest` 34 = 30 + 4, ruff, mypy clean); `git commit --no-edit` → two-parent `dd3293d`. | Transcripts on the page. | M17 p2 |
| After the push, PR #5: `MERGEABLE`/`CLEAN`, 5 files, commits `37d4731 3b9501a dd3293d`; `GET /pulls/5/commits` shows `dd3293d` with 2 parents — the artifact `check_a3.py` reads. | Live. | M17 p2, `check_a3.py` |
| A fixture-based conflict was tried first and rejected as dishonest: tagging a card in the shared `sample_deck` fixture breaks the storage round-trip test until tag persistence (T08) lands, so no careful T07 author would do it. The conflict was moved to the model docstring and the test file's tail, where both tickets had a real reason to be. | Local run; the branch was reset before anything was pushed. | — |

#### Skills — installed versus upstream

| Fact | Evidence | Page |
|---|---|---|
| The installed `~/.agents/skills/` copies are dated **2026-07-09**; 38 skills. | `ls -la`. | M18 p1 |
| **`request-refactor-plan` no longer exists upstream**: removed by commit `c66bdee` (2026-08-05, "chore: remove six unused skills and the personal bucket"); raw URL 404 under every bucket. Still installed; M18 quotes the installed file and says so. | GitHub search API + raw fetch. | M18 p1, p2 |
| Upstream buckets as of 2026-09-13: `engineering` (ask-matt, code-review, codebase-design, diagnosing-bugs, domain-modeling, grill-with-docs, implement, improve-codebase-architecture, prototype, research, resolving-merge-conflicts, setup-matt-pocock-skills, tdd, to-spec, to-tickets, triage, wayfinder, wizard), `productivity` (grill-me, grilling, handoff, teach, to-questionnaire, wait-what, writing-for-agents), `misc` (git-guardrails-claude-code, migrate-to-shoehorn, scaffold-exercises, setup-pre-commit), `in-progress` (claude-handoff, implement-spec, loop-me, retro, …), `deprecated` (empty by policy). | `GET /repos/mattpocock/skills/contents/skills/<bucket>`. | M18 |
| Upstream front-matter descriptions of the seven surviving skills are word-for-word the installed ones except `wayfinder`, whose em-dashes became parentheses on 2026-08-19 ("Remove all em-dashes from the repo"). The README's one-line descriptions differ from the front matter (e.g. `resolving-merge-conflicts`: README "Work through an in-progress git merge or rebase conflict hunk by hunk…" vs front matter "Use when you need to resolve an in-progress git merge/rebase conflict."). Pages quote the front matter. | Raw `SKILL.md` fetches diffed against installed. | M18 p2 |
| `grill-me`'s body is one line, "Run a `/grilling` session."; `disable-model-invocation: true` on ask-matt, wayfinder, grill-me, handoff; absent on resolving-merge-conflicts, request-refactor-plan, tdd, git-guardrails. | Files. | M18 |
| `resolving-merge-conflicts` is therefore model-invocable — it can start on its own when a merge stops. | Front matter. | M17 p2, M18 p1 |

#### Checker and site

- `checkers/check_a3.py` (new) grades: ≥ 2 merged PRs linking issues; a blocking edge among
  them; head branch starts with the linked issue's number; the four body headings; a closing
  keyword in the body; linked issues `CLOSED`/`COMPLETED` within 30 s of the merge; a merged PR
  with a base change onto the default branch (`BaseRefChangedEvent` **or**
  `AutomaticBaseChangeSucceededEvent`), whose parent is a merged PR and whose issue is blocked
  by the parent's; a two-parent commit on that PR; an issue with a closed-unmerged PR followed
  by a smaller merged one; `a3-writeup.md` (≥ 200 words; mentions "conflict"; names ≥ 3 of the
  six skills — notes). Against `flashcards-w3probe` it fails on exactly the write-up; against
  `flashcards-seed` it stops at "0 merged PRs that link an issue"; a nonexistent handle fails
  "Instance exists". **Fault-injected 13/13** by replaying a recorded snapshot of the live `gh`
  responses with one mutation per rule (`fault_a3.py` in the session scratchpad).
- `checkers/check_site.py`: Evaluate pages now also require a hands-on checklist (M14 is the
  first Evaluate objective with pages); verified by injection. **42 pages, 462 internal links,
  clean.**
- Self-checks: 40 questions on the 14 Week 3 pages, written and then rebalanced with the
  audit's option-form scan (correct option never uniquely longest, shortest, or the only one
  with `<code>`): 25 flagged on the first pass, **0 after** four rounds of distractor edits.
  Answer letters 12/10/8/10 across A–D.
- Render: the Chrome extension was not connected this session, so the pages were driven in
  **headless Chrome** (`--headless=new --virtual-time-budget`) from a same-origin iframe
  harness at 1200 px and 400 px: 4 Mermaid diagrams drawn on 4 pages, 14 decks built and run to
  "complete" with the list hidden, 40/40 self-checks mark wrong-then-right correctly with the
  first-try tally at 0/N, no in-frame errors, **no horizontal overflow at either width**. One
  page screenshotted at 1200 px and read by eye. The harness file was deleted before commit.
- `docs/assets/styles.css`: a `.tier.anc` chip for the ancillary source on the M14/M16 pages,
  and a `blockquote` rule (first use, M15 p2).

**Left over for the instructor:** `perro-ruidoso/flashcards-w3probe` (private, 3 issues, PRs
#4–#11, `delete_branch_on_merge` restored to false) joins `flashcards-w2probe` on the delete
list; same `delete_repo` refresh, then `gh repo delete perro-ruidoso/flashcards-w3probe --yes`.
Nothing on the pages depends on it surviving. Not done: the Linear branch-name link, live (M13
p2 says so); the two untested branch-deletion paths (M16 p3 says so).

### Weeks 1–3 audit — 2026-09-14

Hostile re-check of everything shipped for Weeks 1–3, run with the tools live on `gh`
2.100.0, extending the 2026-09-13 audit to Week 3 and adding the cross-week pass no audit
had done. Filed as issue **#19** (blocked by #17); branch `19-audit-weeks-1-3` made with
`gh issue develop 19 --name 19-audit-weeks-1-3 --base 17-week3-pages --checkout` at
12:17 UTC, which wrote `branch.19-audit-weeks-1-3.gh-merge-base = 17-week3-pages` — the M13
move on the course repo. Preconditions checked first: **#16 was still open** (base `main`,
`closingIssuesReferences` → #15) and **#18 still based on `15-audit-weeks-1-2`** with
`closingIssuesReferences: []` at 12:26 UTC, so the retarget the brief asked for could not be
done; the *before* state is recorded on M06 p3 and M16 p2 instead (below). Both throwaways
exist (`flashcards-w2probe`, `flashcards-w3probe`, private). The Chrome extension was not
connected; rendering ran in headless Chrome as on 2026-09-13.
Each row: **fact · evidence · page · fixed or open.**

#### 1. Sources — every URL re-fetched, every quotation re-checked, every skill re-diffed

105 distinct external URLs across the three hubs, all 39 Learning Pages, Course Home, and
`RESOURCES.md` were fetched with `curl -sL` and their status, effective URL, and redirect
count recorded. **All 105 answered 200 with zero redirects** — no new URL rot since the 13th.
Then every quoted span of four words or more outside `<pre>` (621 spans; curly and straight
quotes paired separately) was searched, alphanumeric-only and fragment-by-fragment across
`…`, in the fetched text of the sources its page links, then in the installed `SKILL.md`
files, then in the course's own documents; the 199 survivors were read by hand (prompts,
answer options, transcript strings, and the course's own phrases in quotation marks).

| Fact | Evidence | Page | Status |
|---|---|---|---|
| Every GitHub Docs, `gh` manual, git-scm, Linear, Google, and Anthropic quotation is present verbatim, including the three the scan could not match because of a bracketed edit (`focus[es]`, `create[s]`, `stop[s]`). | Hand check against the fetched text. | all | Verified. |
| **One Anthropic sentence has grown.** M18 p1 quoted "…set `disable-model-invocation: true` in its frontmatter." with a full stop; the page now continues ", or “user-invocable-only” in skillOverrides when you don’t want to edit the file." | code.claude.com/docs/en/skills, fetched 2026-09-14. | M18 p1 | **Fixed** — quoted in full. |
| M06 p1 quoted PR #14's body as "Closes #13. Stacked on #12 — the base branch is …" and dropped "(the Week 1 rebuild)" without an ellipsis. | `gh pr view 14 --json body`. | M06 p1 | **Fixed** — quoted as written. |
| M15 p1 cut the commit message after "Nothing reads or writes them yet" (the line continues "; that is #2 and the scheduler ticket"), and called it "missing three of the four sections" — it carries a hint of Scope. | `gh api repos/…/pulls/4/commits`. | M15 p1 | **Fixed** — full sentence; "nothing under Verification or Risk". |
| M16 p1 said PR #5's Intent section "opens" with the stacked-on sentence; it is the section's second sentence. | `gh pr view 5 --json body` on w3probe. | M16 p1 | **Fixed**. |
| M17 p2 presented three lines of the Seed `CLAUDE.md` Commands block as one quoted sentence with semicolons. | `gh api repos/…/flashcards-seed/contents/CLAUDE.md`. | M17 p2 | **Fixed** — shown as the three command lines. |
| M07 p2 cut a Seed criterion at "bare `round()` is wrong" — the line ends "and `docs/adr/0001` says why". | `gh issue view 3 -R flashcards-seed`. | M07 p2 | **Fixed** — quoted to the end. |
| M12's Linear property list and the Seed criteria on M07 p2 use em-dashes where the sources use hyphens or bullets; words identical. | Fetched text. | M07 p2, M12 | Left; noted so nobody "corrects" them. |

**Skills — installed (`~/.agents/skills/`, 38 files dated 2026-07-09) versus upstream
(`mattpocock/skills` head `3cca18b`, 2026-09-04), re-diffed file by file.** The 2026-09-13
note that upstream descriptions were "word-for-word the installed ones except `wayfinder`'s
em-dashes" was **false on the day it was written** — it must have compared only the last
commit. What is actually different, with the commit dates:

| Fact | Evidence | Page | Status |
|---|---|---|---|
| **`qa` was removed upstream in the same commit as `request-refactor-plan`** (`c66bdee`, 2026-08-05), "each already absorbed by a promoted skill". The changeset names the replacements: `qa` → `/triage` and `/to-tickets`; `request-refactor-plan` → `/to-spec` and `/improve-codebase-architecture` (the open question below had guessed `implement`). `ubiquitous-language` → `/domain-modeling`; `design-an-interface` → `/codebase-design`. The same commit removed `qa` from `setup-matt-pocock-skills`'s issue-tracker explainer. | `gh api repos/mattpocock/skills/commits/c66bdee`; `.changeset/remove-deprecated-and-personal.md` (its text now lives in upstream `CHANGELOG.md`, which also says "None of them was in the Claude Code plugin"); raw-URL 404 under every bucket. | M05 p1, M18 p1/p2, M24's primary source | **Fixed on the pages** (M05 p1 caveat; M18 names the replacements). **Open:** what Week 4 names for M24, and whether M18 swaps the skill — see suggestions. |
| **The plugin students install carries 25 skills, not 38.** `.claude-plugin/plugin.json` v1.2.3 lists the `engineering` and `productivity` buckets only: no `request-refactor-plan`, no `qa` (deleted), no `git-guardrails-claude-code` (`misc`, "not promoted in the plugin"), no `claude-handoff` (`in-progress`). `student-setup.md` says "Use the plugin." So a student following the handout cannot run two of M18's six named skills, nor M24's. The course machine's `~/.agents/skills/` is an older, fuller `npx skills` snapshot. | Manifest fetched 2026-09-14; handout line 136. | M18 p1/p2, A3 item 6, student-setup | **Fixed on the pages** (a "What the plugin gives you" box; each skill header says whether it is in the plugin; `git-guardrails` can be added alone with `npx skills@latest add`). **Open:** pin a version or track the plugin — suggestion below. |
| `wayfinder`'s description says "decision tickets" upstream, "investigation tickets" installed — renamed 2026-07-13, four days after the snapshot, not merely re-punctuated. | Raw file diff; `commits?path=`. | M18 p1 ("Same words" — false), M18 p2 | **Fixed** — both quoted, dated. |
| `grilling` was rewritten upstream between 2026-07-13 and 2026-08-20: description now "…about a plan, decision, or idea. Use when the user wants to stress-test their thinking…"; body works the design tree in numbered rounds with a recommended answer under each question. M18 p2 quotes the installed one-question-at-a-time body. | Raw file diff (installed 12 lines, upstream 28). | M18 p2 | **Fixed** — installed text kept, upstream change described and dated. |
| `grill-me`'s body became "Call the Skill tool with "grilling"." on 2026-08-15 (`fcf0071`); `grill-with-docs` and `handoff` got the same "Skill tool" phrasing. | Raw file diff. | M18 p2, self-check Q2 | **Fixed** — noted; Q2 now says "the course machine's installed file". |
| **`ask-matt` was rewritten on 2026-08-05** (`fa1e322`): the smart zone is "~150k tokens" (was ~120k); "Crossing sessions" became "Phase boundaries", which ranks five options and makes `/compact` "The default" and `/handoff` "Narrow: only for a new harness, a new directory, a colleague, or forking a side task mid-phase" — the reverse of the installed advice M18 p1 quoted ("`/handoff` and continue in a fresh thread"); `/resolving-merge-conflicts` now appears under Standalone (M18 p1 said "not on the map at all"); `wizard`, `to-questionnaire`, `wait-what` were added. | Raw file diff; commit list. | M18 p1 (three sentences), M18 p2 `handoff`, M18 p2 Q4, A3 item 6 | **Fixed** — M18 p1 quotes both versions with dates; the `handoff` entry, Q4, and A3 situation 2 were rewritten around a case both routers agree on (work continuing in another directory or with a colleague) so the objective does not depend on which copy a student has. |
| `to-tickets` description: "edges as text in one file per ticket locally" (2026-07-10); `to-spec` dropped "(you may know this document as a PRD)" (2026-08-03); `code-review` description says "issue/spec" not "issue/PRD" (2026-08-03); em-dashes → colons/commas repo-wide (2026-08-19); descriptions with colons now YAML-quoted (2026-08-19); `disable-model-invocation: true` added to `grill-with-docs`, `implement`, `setup-matt-pocock-skills`, `triage`, `claude-handoff` (2026-08-15). None of these changes a sentence the pages quote as fact. | Diffs. | M09, M10, M03 p2 | Verified; recorded here. |
| `code-review`'s "three-dot, so the comparison is against the merge-base" line, `resolving-merge-conflicts`'s description and five steps, `tdd`'s seam rule, `handoff`'s description, and `git-guardrails`'s description and block list are unchanged in wording. | Diffs. | M03 p2, M17 p2, M18 p2 | Verified. |
| `deprecated/README.md` and `misc/README.md` sentences quoted on M18 p1 are present verbatim; the commit message "chore: remove six unused skills and the personal bucket" is exact. | Raw fetch; `gh api …/commits/c66bdee`. | M18 p1 | Verified. |

#### 2. Transcripts — every printed `gh` command re-run

Every read-only command on every page was re-run at 12:26–12:40 UTC on 2026-09-14 against
`cli/cli`, `perro-ruidoso/gh-pr-mastery`, `flashcards-seed`, `flashcards-w2probe`, and
`flashcards-w3probe`, and diffed against the page. Mutations on the throwaways (the sub-issue
move, the cycle, the probes, `gh pr merge`, the closes) were **not** re-run; the pages call
the repositories throwaways and the state they left behind was read instead.

| Fact | Evidence | Page | Status |
|---|---|---|---|
| `gh pr list -R cli/cli --limit 3` moved again: **#14437** (same-repo, opened 09:20 that morning) is on top; #14373 (fork) and #14355 (draft) remain; #14351 fell off. One fork head of three, as the prose says. | Live 12:26 UTC. | M02 p2, M04 p1 | **Fixed** — re-captured, dated 2026-09-14, the movement described in the prose. |
| `gh pr list --limit 1 --json number --jq '.[0].number'` prints **14437**, not 14373. | Live. | M04 p2 transcript and self-check Q3 | **Fixed** — transcript re-captured with both days' values; the question now asks about "a bare number" rather than a fixed one. |
| `gh issue list -R cli/cli --limit 3`: **#14439** new on top (`needs-triage`); #14413 fell off. | Live. | M04 p2 | **Fixed** — re-captured. |
| `cli/cli#14398`: still `CLOSED`, `closedAt 2026-09-13T06:06:03Z`, 2/0/1, same refs; `--json nope` still lists 46 fields; `gh pr diff 14373 --name-only` → `docs/install_linux.md`; `#14404`/`#14429` identical to the page. | Live. | M02 p1, M04, M06 p1 | Verified. |
| **The course-repo snapshot on M06 p3 had gone stale again in one day.** Open issues are #15, #17, **#19** (this audit); open PRs #16 (→ #15) and #18 (stacked on #16's branch, `closes []`); recorded edges are now **four** — #2←#1, #13←#11, **#17←#13**, **#19←#17** — where the page said "exactly one more"; the number lists lacked 17/19 and 16/18. The merged list (seven PRs) had not changed. | `gh pr list`, `gh issue list`, `dependencies/blocked_by` for every issue. | M06 p3 | **Fixed** — snapshot re-captured and dated; the open pair is now shown as the *before* state of a stack (`Closes #17` in the body, link empty) that M16 p2 also records with the 11:50:18Z / 12:26Z timestamps and the `gh pr view 18` command to run. |
| `#14`'s `gh pr view`, timeline, GraphQL `BaseRefChangedEvent`/`HeadRefForcePushedEvent`/`MergedEvent`, #12's `mergedAt`/`cf6d380`, #11's and #13's `closedAt` — all identical. #13's REST timeline has still no `connected` event. | Live. | M06 p1, M16 p2 | Verified. |
| Seed Repo: issue #1's body, the four criteria on M07 p2, the 15-issue listing, `waves_from_github.py` (15/19/joins #5 #7 #9 #13 #14/waves 1-3-4-4-3/width 4; `--mermaid` output identical), #14's `blocked_by` with ids, no labels/type, `parent` → 404, the ten default labels, `isTemplate: true`. | Live. | M07, M10 p2, M11 p2, M01 p2 | Verified. |
| `flashcards-w2probe` read-only commands (label queries, `--type Task`, `--search` forms, template listing, #5's parent/blockedBy, #1's subIssues, #2's `blocking`, database id `5440629998`, `waves_from_github.py` and `--mermaid`, probe #7 closed/completed with one comment): every output identical to the page. | Live. | M08 p1/p2, M11 p1/p2, M12 p2 | Verified (first time these were re-run; the 09-13 audit skipped w2probe). |
| `flashcards-w3probe`: `gh issue develop --list 1` empty; PR #4's `--name-only`, `--json files`, and the full diff (md5 `8cea3fec…`); PR #6's seven files and counts; #3 → `prs [7]` (now `CLOSED`, as the page's "before #7 merged" comment allows); PR #5's `BaseRefChangedEvent` 17:03:12; #2's `connected` 17:03:13; the three `closedAt` one second after each `mergedAt`; `#5`'s timeline four events; `dd3293d` with two parents; PR #7's body; probes #8–#11 timelines and the `AutomaticBaseChangeSucceededEvent` 17:15:53; `delete_branch_on_merge: false`. | Live. | M13–M17 | Verified. |
| `issue.linkedBranches` on w3probe #1 and #3 now returns **`[]`** — the page shows the branch name, captured before PR #4 existed. | GraphQL. | M13 p1 | **Fixed** — dated note under the transcript: the relation moved to the PR, as the page's next section says. |
| A **merged** PR reports `mergeable: UNKNOWN` / `mergeStateStatus: UNKNOWN`, permanently: a student re-running M17 p1's command on PR #5 sees the page's middle value again for a different reason. | `gh pr view 5 --json mergeable,mergeStateStatus` on w3probe. | M17 p1 | **Fixed** — dated note; read `state` beside it. |
| PR #11's timeline gained `commented`, `closed`, `head_ref_deleted` (17:16:30–34) after the probe; `probe-child` is the one probe branch still on the repository (the page said four branches "restored"). | REST timeline; `gh api repos/…/branches`. | M16 p3 | **Fixed** — sentence extended. |
| PR #5's final shape is 5 files, +99 −9, commits `37d4731 3b9501a dd3293d`. | Live. | M17 p2 (shows `changedFiles: 5`) | Verified. |

#### 3. Checkers — run, then fault-injected rule by rule

- `check_site.py`: **42 pages, 462 internal links, clean** before the audit. **New rule, from a
  real defect:** nine relative links (`../../assignments/a1.md`, `adr/0003`, `adr/0004`,
  `CONTEXT.md`, on the three hubs and M01 p2, M02 p2, M05 p2, M06 p3) resolve on disk and
  passed the checker, but GitHub Pages serves `docs/` alone, so on the published site every
  one was a **404** (`curl` → 404 for `…/gh-pr-mastery/assignments/a1.md`). All nine now point
  at the GitHub blob URLs, and `check_site.py` refuses any relative link whose target is
  outside `docs/`. **28 faults injected** into a scratch copy, one per rule — the 25 from the
  last audit, the Create- and Evaluate-checklist cases, and the new escaping-link rule —
  **28/28 caught on the first run**. After the fixes: **42 pages, 453 internal links, clean.**
- `check_a1.py` / `check_a2.py` / `check_a3.py` against `flashcards-seed`, `flashcards-w2probe`,
  `flashcards-w3probe`, and `flashcards-nonexistent-zz`: each fails on exactly what the
  target lacks and stops at *Instance exists* for the nonexistent handle; all three exit 1 on a
  failure. `check_a3.py` on w3probe still passes every rule but `a3-writeup.md`. One nuance
  recorded: `check_a2.py`'s *Every open issue has a label / has a type* pass **vacuously** on a
  repository with no open issues (w3probe), because the rules quantify over open issues.
- `check_a3.py` fault-injected by **snapshot replay** (`fault_a3.py`, rebuilt this session:
  record the eight `gh` calls the checker makes against w3probe, replay them with one JSON
  mutation per rule): **16/16** rules reported by name — the 13 from the 13th plus the three
  write-up rules, exercised with a synthetic write-up whose positive control passes every rule.
- `check_a1.py` / `check_a2.py` fault-injected by **live mutation** on `flashcards-w2probe`
  (`fault_a12.py`; each mutation reverted and the final run compared to the baseline):
  **22/22** reported by name — delete `needs-info`; delete `wontfix`; add then remove
  `docs/agents/issue-tracker.md` (pass → fail); add then remove `## Agent skills` in
  `CLAUDE.md`; a five-word `a1-writeup.md` (length, evidence, cites) then a good one (all pass);
  #4 loses its type; the spec loses `ready-for-agent` and becomes a Task; the mermaid fence
  removed; `layer:cli` deleted; cycle #2←#5; join edge #5←#4 removed (also *Blocked-by lines are
  recorded edges*); probe reopened; probe comment deleted; a template without `type:`, a heading
  missing, and a `tests/` line (three rules); every label removed from #2; a hand ticket without
  a test path; a five-word `a2-writeup.md` with no image; a spec heading renamed (spec not
  found, tickets not found). **One thing the revert did not restore by itself:** `gh label
  delete layer:cli` strips the label from every issue carrying it, and `gh label create` does
  not put it back — #5 had to be re-labelled by hand. Worth knowing before grading a student who
  "recreated" a label. The throwaway now carries a run of `audit fault injection` / `audit
  fault revert` commits on `main` and one more closed probe issue (#9); nothing on the pages
  depends on either.

#### 4. Render — every page, headless Chrome, 1200 px and 400 px

Chrome extension not connected. A same-origin iframe harness (`docs/_harness.html`, deleted
before commit) served over `http.server` and driven by `chrome --headless=new
--virtual-time-budget=240000 --enable-logging=stderr --dump-dom` at each width; a deliberate
`console.error` + `ReferenceError` probe page confirmed the console channel captures both.

| Check | 1200 px | 400 px |
|---|---|---|
| Mermaid diagrams drawn (10 across 9 pages), no error text | 10/10 | 10/10 |
| Decks built and run to "Deck complete" with the list hidden and a `localStorage` record (38 decks, 286 cards) | 38/38 | 38/38 |
| Self-checks: wrong first click marks `.incorrect` with the rationale hidden; correct click reveals it; tally `0 / N` after a wrong-first pass (133 questions) | 133/133 | 133/133 |
| Console messages / in-frame `error` events | none | none |
| Horizontal overflow | none | none |

Re-run after every edit in this audit at both widths: identical totals.

#### 5. Self-checks — option form

133 questions, **0 flagged** (correct option never uniquely longest, uniquely shortest, or the
only one with `<code>`). Answer letters **36 / 33 / 29 / 35** across A–D. Three questions were
rewritten for content, not form (M04 p2 Q3 number-agnostic; M18 p2 Q2 names the copy; M18 p2
Q4 built on a case both routers agree on); the scan is still 0 after the rewrites.

#### 6. Cross-week coherence — read in pager order

| Fact | Evidence | Page | Status |
|---|---|---|---|
| **Contradiction across weeks:** M01 p2's learn-more said the Seed's "15-issue backlog" is "what you are about to inherit"; Week 2 is built on the verified fact that a template copies files, not issues. | The two sentences. | M01 p2 vs Week 2 hub / M07 | **Fixed**. |
| **Term before definition:** "frontier" is quoted from `to-tickets` on M07 p1 and used on M11 p1, and first *defined* on M17 p1 ("Week 2 called this the frontier" — it had not). | grep. | M07 p1 | **Fixed** — glossed where it first appears, tied to M10 p2's waves. |
| "Squash" is used (`gh pr merge --squash`, M15 p2) one page before M16 p2 explains it. | Reading order. | M15 p2 | Open — minor; M16 p2 quotes the definition and A3's notes point there. |
| **Fact stated differently:** M15 p2 called M06's worked-example gap "one second"; M06 p1's is two seconds (`cli/cli`), the course repo's one. | Both pages. | M15 p2 | **Fixed**. |
| M14 p1 said `gh pr diff` has "four flags" (`--name-only --patch --exclude --web`); the manual lists six (plus `--color`, `--allow-escape-sequences`); M04 p2's learn-more listed a different four. | Fetched manual. | M14 p1, M04 p2 | **Fixed** — six named, dated. |
| The instructor guide's toolchain table says `gh` **2.60+**; the handout, Week 2 hub, and M08 say 2.94.0+. | Guide 2.1 vs `student-setup.md` line 48. | Guide | **Fixed**. |
| M02 p2 self-check Q1 abbreviated a head to `clean-git-test-seams`; the listing shows `williammartin-clean-git-test-seams`. | Page. | M02 p2 | **Fixed**. |
| M05 p2's checklist said the checker verifies "the five labels exist"; it grades four and notes `wontfix`. | `check_a1.py`. | M05 p2 | **Fixed**. |
| M18 p1 said "You have used six of the installed skills so far" and listed four plus two "soon". | Page. | M18 p1 | **Fixed**. |
| Guide 8.3: "Most of the four merged PRs have no recorded blocker" — seven merged PRs, four edges. Guide header: "Weeks 2–6 do not exist yet". Guide 2.4: expected `check_site.py` output "8 pages, 67 internal links". Guide Part 9 item 10: "Not built yet: Weeks 2–6 and assignments A2–A6". | Guide. | Guide | **Fixed** — each dated. |
| **Ask-your-teacher prompts that assume tools a student may not have:** M18 p2's asks the student to "open each chosen skill's installed `SKILL.md`" — two of the six are not in the plugin. Every other prompt assumes only Claude Code, `gh`, and (M12/M13 p2) the Linear workspace the course requires. | Reading. | M18 p2 | **Fixed** — the page now says which two are absent and how to add one; the prompt stands for the four. |
| **Flashcards whose back is not on the page:** a scripted pass over all 286 cards (every `<code>` span and number on a back looked for elsewhere on its page) flagged 18, all generalised command forms (`N`, `O/R`, `<handle>`) whose concrete instances are on the page; none states a fact its page does not. | Script; hand reading. | all | Verified. |
| **Hands-on items no assignment exercises** (by design, listed so the instructor can decide): M03's four-minute experiment (Quiz 1 objective); M04 p2 "largest open PR on a repository I care about"; M06 p2 "the method on a repository I did not choose"; M08 p2 "opened `gh issue create --web`"; M11 p1 "repeated the two-parent experiment on my own tickets"; M13 p2 "wrote the convention into `CLAUDE.md`" and the Linear-ID half of the branch name (A3 reads only the leading number); M15 p2 "read the `connected` event"; M16 p3's probes (the page says so). | Reading A1–A3 against every checklist. | — | Recorded. |
| **Assignment items no page teaches:** none. Every command in A1–A3 appears on a page; the one out-of-order use is A2 item 5's `gh pr close`, taught on M14 p2 (Week 3) and used in Week 2's Linear preview. | Reading. | A2 | Recorded; minor. |
| **Checkers vs rubrics vs what pages say:** every "the checker verifies…" sentence on M05–M17 matches the code, with two precisions — M11 p1 says the checker verifies "every ticket has the spec as its parent" (it counts the tickets that do; one without a parent is silently not a ticket), and M12 p2 says it "looks for the capture file" (it looks for an image reference, as a note). A1–A3's "Graded:" lines match the rule lists. | `check_a1/2/3.py` read against the pages. | M11 p1, M12 p2 | Recorded; wording left. |
| `check_a2.py` passes *Every open issue has a label/type* vacuously on a repo with no open issues. | w3probe run. | — | Recorded (a student with tickets is never in that state). |

#### 7. The course repo as exhibit, 2026-09-14

At 12:26 UTC: PR #16 open (base `main`, closes #15); PR #18 open, base `15-audit-weeks-1-2`,
`closingIssuesReferences: []`, body "Closes #17. **Stacked on #16**…" (created 11:50:18Z);
issue #19 filed 12:16:51Z, blocked by #17; branch `19-audit-weeks-1-3` created from
`17-week3-pages` by `gh issue develop` a minute later. That is a three-deep stack
(#16 ← #18 ← this PR) in the state M15 p2's condition one describes, on a repository every
student can read; M06 p3 and M16 p2 now say so and print the command that will show when it
changes. When #16 merges, #18 and then this PR need `gh pr edit --base main` and the rebase
M16 p2 describes — record the timestamps on M06 p1/M16 p2 when it happens.

#### 8. Suggestions (not done; each needs the instructor's call unless marked)

| # | What | Evidence | Cost | Objective | Decision needed? |
|---|---|---|---|---|---|
| S1 | **Pin the skills the course teaches, or track the plugin.** Either ship `student-setup.md` with `npx skills@latest add mattpocock/skills` (a fixed set, editable, *including* `git-guardrails` and — from a fork or vendored copy — `request-refactor-plan`), or keep the plugin and rewrite M18/A3/M24 around the 25 skills it contains. | §1: plugin manifest; two of six M18 skills and M24's `qa` absent from the plugin; `ask-matt`'s advice reversed upstream. | Half a day either way; the handout, guide 2.3, M18, A3 item 6, and RESOURCES change. | M18, M24, M05 | **Yes.** Recommendation: track the plugin (students get updates; the course stops teaching a stale snapshot) and swap the two absent skills. |
| S2 | **Replace `request-refactor-plan` in M18** with what its own changeset names — `/to-spec` + `/improve-codebase-architecture` — or with `/improve-codebase-architecture` alone (in the plugin, on `ask-matt`'s map under Codebase health). | §1: changeset `remove-deprecated-and-personal.md`. | Two hours: one M18 p2 section, objective text in `build_objectives.py`, A3 item 6's first situation, `check_a3.py`'s skill list. | M18 | **Yes** (was already open; the evidence is now specific). Recommendation: `improve-codebase-architecture`. |
| S3 | **Name M24's skill now.** `/qa` is gone upstream; the changeset says `/triage` + `/to-tickets`. Week 4 is unbuilt, so the cost is one objective row and one primary source. | §1. | Minutes now; a page rewrite later. | M24 | **Yes.** |
| S4 | **Label and type the Seed backlog** (`layer:*`, `Task`) — or leave it as M08's exhibit of an unclassified backlog. Judgement: leave it. M08 p1 uses the gap deliberately ("try to find its domain-layer tickets without reading every body"), A2 item 1 has students classify their *own* backlog, and labelling the Seed would remove the only unclassified backlog students see. If labelled, M08 p1's last callout and A2's "compare with the Seed" lose their point. | M08 p1; A2 item 1. | An hour to label; two page edits. | M08 | **Yes**, but the recommendation is no. |
| S5 | **M13 p2's Linear half stays documentary until a workspace exists** — the same standing as M12, and the same five-minute live check would settle both. Nothing else on the page depends on it, and A3 reads only the leading number. Do the M12 walk first; fold this in. | M12 p1, M13 p2 "Not run live". | Five minutes once a workspace exists; two dated captures. | M13, M12 | No — already decided to keep documentary; needs the workspace. |
| S6 | **A `--handles` batch exercise.** All three checkers accept `--handles FILE` and `--json`, and the guide's 8.1 shows the form, but no run in any audit has exercised it, and the guide's calibration advice assumes single runs. One run against a three-line file (`seed`, `w2probe`, `nonexistent-zz`) each cohort would catch a regression in the loop or the exit code before grading night. Judgement: worth doing and cheap; a `checkers/handles.example` file would make it a one-liner. | `main()` in each checker. | Twenty minutes. | Grading (A1–A3) | No — do it in the next unit. |
| S7 | **Part 7 live-demo scripts for Weeks 2 and 3.** Week 1 has 7.2–7.4 with real output; Weeks 2–3 have Part 10 bullets ("live demo the retarget", "let the conflict happen") with no script or expected output. The Week 3 pages already contain every command and output a demo needs, so the script is a compilation, not new research; Week 2's would be the M11 two-parent experiment and the cycle. Judgement: yes for Week 3 (the retarget and the conflict are the two moments that surprise people and both are ten-minute demos); Week 2's can be the M11 p1 transcript read aloud. | Guide Part 7 vs Part 10. | Two hours for both. | M11, M16, M17 | No — build it with Week 4. |
| S8 | **Delete the two throwaways.** Nothing on any page depends on either surviving (every transcript is printed); both are private; w2probe now carries audit commits and a ninth issue. The build token still lacks `delete_repo` (`gh auth status`, 2026-09-14). **Ask before deleting** — the command is in Part 10. | `gh repo list perro-ruidoso`. | One `gh auth refresh -s delete_repo`, two `gh repo delete --yes`. | Hygiene | **Yes** — needs the scope and the go-ahead. |
| S9 | **Bring the plugin/skills drift into the audit checklist.** Add "re-diff installed vs upstream vs plugin manifest" to Part 10 item 3 and to the next audit issue, since the 13th's check missed it. Done in this unit for the guide. | §1. | Done. | — | No. |

**Claims that turned out to be false** (the PR body repeats this list): every upstream
description was "word-for-word" the installed one except `wayfinder`'s punctuation (`wayfinder`,
`grilling`, `to-tickets`, `code-review`, `to-spec` differ in words); `request-refactor-plan` is the
only named skill gone upstream (`qa` went in the same commit); "still installed and still runs"
applies to students (the plugin never had it); `resolving-merge-conflicts` is "not on the map at
all" (it is, upstream, since 2026-08-05); the smart zone is ~120k tokens (upstream: ~150k); the
router's advice for a nearly full window is `/handoff` (upstream: `/compact`); the Seed's
15-issue backlog is "what you are about to inherit"; the course repo has exactly two recorded
edges and one open issue with no PR; `gh pr list --limit 1` prints 14373; the top three open
PRs on `cli/cli` are #14373/#14355/#14351; `gh pr diff` has four flags; "Week 2 called this the
frontier"; M06's worked-example gap is one second; the instructor guide's `gh` minimum is 2.60;
the guide's `check_site.py` expected output is "8 pages, 67 links"; the nine `../../` links to
the assignments, ADRs, and `CONTEXT.md` work on the published site (they 404); `check_site.py`
was clean in the sense that mattered (it accepted those links); PR #5's Intent "opens" with the
stacked-on sentence; the Seed `CLAUDE.md` "names them" in one sentence; four probe branches were
restored on w3probe (`probe-child` remains).

### Week 4 — owning the diff — verified 2026-09-14

Everything below was **run**, not read, on the Week 3 throwaway `perro-ruidoso/flashcards-w3probe`
(private) with `gh` 2.100.0, git 2.52.0, Python 3.14, Claude Code (Opus 5), between 13:24 and
13:55 UTC, plus one run of the planting script on `flashcards-w2probe`. Filed as **#21**
(blocked by #17 and #19); branch `21-week4-pages` from `19-audit-weeks-1-3` via `gh issue
develop` (13:15 UTC) — stacked on #20, which is stacked on #18, which is stacked on #16. The
brief said to stack on `17-week3-pages` if #18 was unmerged; the audit branch on top of it
carries the `check_site.py` rule and the NOTES/guide edits this unit extends, so the tip of the
stack was used and the PR body says so. The transcripts on the Week 4 pages are these runs
verbatim; the session's full log is `transcript-w4.txt` (scratchpad, not committed).

#### Sources — every URL fetched before writing

The one existing Week 4 row (reviewing proposed changes) answered 200 with no redirect. Seven
URLs new to the course redirected once each and are recorded canonically in `RESOURCES.md`:
commenting, incorporating feedback, approving with required reviews, dismissing a review
(`collaborating-with-pull-requests/reviewing-changes-in-pull-requests/…` →
`how-tos/review-pull-requests/…`); requesting a review (→ `how-tos/create-pull-requests/…`);
"About pull request reviews" (→ `pull-requests/reference/pull-request-reviews`); and **the
GraphQL reference has been regrouped by domain** — `graphql/reference/mutations` and
`graphql/reference/objects` both redirect to the bare `graphql/reference` index, and
`resolveReviewThread`, `PullRequestReviewThread`, `PullRequestReviewDecision`, and
`ReviewRequestedEvent` all live on `graphql/reference/pulls`. The REST pages (reviews, review
comments, issue comments, timeline, event types), the five `gh` manual pages, code.claude.com's
Code Review page, Google's reviewer-comments page, and `super-memory.com/english/ol/sm2.htm`
answered 200 with no redirect. Three course-repo blob URLs on the pages (`skills/qa/SKILL.md`,
`skills/README.md`, `assignments/a4.md`) are **404 until this PR merges**; every other external
URL on the 14 pages answered 200.

| Fact | Source |
|---|---|
| "Pull request authors cannot approve their own pull requests." | Reviewing proposed changes |
| "The **Request changes** option is purely informational and will not prevent merging unless a ruleset or classic branch protection rule is configured with the 'require a pull request' option." | Reviewing proposed changes |
| "Anyone with read access can review and comment on proposed changes." / "To request a review, you need write access to the repository. You can request a review from a person or team with read access." | Pull request reviews (reference) |
| "You can resolve a conversation in a pull request if you opened the pull request or if you have write access to the repository where the pull request was opened." / "If the suggestion in a comment is out of your pull request's scope, you can open a new issue that tracks the feedback and links back to the original comment." | Commenting on a pull request |
| "Applying one suggested change or a batch of suggested changes creates a single commit on the compare branch of the pull request. Each person who suggested a change included in the commit will be a co-author of the commit." | Incorporating feedback |
| "After someone reviews your pull request and you make changes, you can request another review from the same reviewer." | Requesting a pull request review |
| `gh pr edit --add-reviewer <login>`: "Add or re-request reviewers by their login." The only special value is `@copilot`. | gh manual |
| Create-review `comments[]` accept `path`, `position`, `line`, `side`, `start_line`, `start_side`, `body` — not `subject_type`, which is on the single-comment endpoint only. "The position parameter is closing down." | REST pulls/reviews, pulls/comments (and the live 422 below) |
| `PullRequestReviewDecision`: `APPROVED`, `CHANGES_REQUESTED`, `REVIEW_REQUIRED`. `PullRequestReviewThread`: `isResolved`, `isOutdated` ("outdated by newer changes"), `isCollapsed` ("collapsed (resolved)"), `resolvedBy`. `resolveReviewThread(input:{threadId})` "Marks a review thread as resolved." | GraphQL pulls |
| **Claude Code has a built-in `/code-review`** ("reviews a diff in your terminal … reports correctness bugs and reuse, simplification, and efficiency cleanups"; `--fix`, `--comment`, effort levels, `ultra`) that is not the Pocock skill of the same name. On the course machine the Skill tool lists the installed Pocock skill; the pages teach telling them apart by output shape. | code.claude.com/docs/en/code-review |
| **The SuperMemo SM-2 page says "If interval is a fraction, round it up to the nearest integer."** The Seed's ADR 0001 says the original "does not settle" rounding. The ADR's half-up decision is the binding rule; its claim about its source is wrong. Filed as w3probe#18 by `/qa`; **not fixed in the Seed** (out of this unit's scope — suggestion below). | super-memory.com |
| Installed `code-review` vs upstream `3cca18b`: same process; punctuation, "issue/PRD" → "issue/spec", and "run /setup-matt-pocock-skills" → "tell the user to run" differ. Installed `qa` is byte-identical (CRLF aside) to `skills/deprecated/qa/SKILL.md` at `f958fa1` = `c66bdee^`. Repo licence MIT. | raw fetches; `gh api …/contents/…?ref=c66bdee^`; `gh api repos/mattpocock/skills/license` |
| The plugin manifest (v1.2.3) lists `skills/engineering/code-review`; no `qa`. | `.claude-plugin/plugin.json` |

#### The exhibit: T03, then the planted refactor

| Fact | Evidence | Page |
|---|---|---|
| T03 filed as w3probe#12 (`--blocked-by 1`, a closed blocker — accepted), branch `12-sm2-scheduler` via `gh issue develop`, implemented per ADR 0001 (EF update then floor; failure keeps EF; `math.floor(x+0.5)` with floor 1), 15 tests, PR #13 with a four-section body; CI lint 6 s / test 17 s green; squash-merged 13:27:53Z; #12 closed `COMPLETED` **13:27:54Z**. | `gh pr view 13`; `gh issue view 12`. | M19 p1 (context) |
| `closingIssuesReferences` on #13 was **populated in the same second the PR was created** (13:26:50Z) — not the one-to-fifteen-second lag Week 3 saw. Both happen. | `gh pr view 13 --json closingIssuesReferences` immediately after `gh pr create`. | — |
| Where the ADR is silent — whether `I(n)` uses the EF before or after this review's update — T03 uses the updated value and says so in the docstring and PR body. `test_third_success…` uses grade 4 (delta 0) so it holds either way. | `scheduler.py`, PR #13 body. | — |
| `Card.__post_init__` rejects `ease_factor < 1.3`, so planted bug 1 (clamp before update) manifests as `ValueError` from `replace()` on the 9th consecutive grade-3 review from 2.5 (2.5 − 9×0.14 = 1.24), not as a stored bad value. | `python -c` probe on the planted branch. | M21 p3 |
| The planted refactor (w3probe#14 "Simplify the scheduler", branch `14-simplify-scheduler`, **PR #15**, commit `b0fac63`, 13:30:43Z) carries the three §7 bugs, deletes the helpers and three constants, keeps a docstring that promises the rules, and rewrites four tests (floor test → single grade-5 pass; two failure tests → 2.5; exact-half → 35.4 → 35). **48 tests pass**; lint, format, mypy clean. The body claims "the rules themselves are unchanged". | PR #15 diff, 2 files, +29 −71. | M19–M23 |
| The `docs/agents/*` files and the four triage labels were added to w3probe `main` first (commit `309b051`), so `/code-review` step 2 could find the issue tracker. `main` then moved again (`bba30dd`, the review-bot workflow); the three-dot diff's merge base is `309b051`. | `git merge-base`. | M21 p1 |

#### Review mechanics (M19/M20)

| Fact | Evidence | Page |
|---|---|---|
| **An author cannot approve or request changes on their own PR**, by either route. `gh pr review 15 --approve` → `failed to create review: GraphQL: Review Can not approve your own pull request (addPullRequestReview)`; `--request-changes` → `… Can not request changes on your own pull request …`; REST `POST …/pulls/15/reviews -f event=APPROVE` → 422 `["Review Can not approve your own pull request"]`; `event=REQUEST_CHANGES` → 422 `["Review Can not request changes on your own pull request"]`. A `COMMENT` review is accepted. | Live, 13:31:31Z. | M19 p1 |
| **Requesting a review from yourself is a silent no-op**: `gh pr edit 15 --add-reviewer acatlin` exits 0 and prints the URL; `reviewRequests` stays `[]`. | Live. | M20 p1 |
| A Conversation-tab comment is an issue comment: read back from `/issues/15/comments` (id 5664781550, 13:31:29Z); never at `/pulls/15/comments`. | Live. | M19 p1 |
| Create-review with a comment on a line outside every hunk → 422 `"Line could not be resolved"`. With `subject_type: file` in the `comments[]` array → 422 `Variable $comments of type [DraftPullRequestReviewComment] was provided invalid value for 0.subjectType (Field is not defined on DraftPullRequestReviewComment), 0.position (Expected value to not be null)` — the REST route is a GraphQL mutation underneath, and file-level comments exist only on the single-comment endpoint. | Live, two attempts. | M19 p2 |
| A comment on a deleted line anchors with `side: LEFT` and the **old** line number (`import math`, LEFT 15). | Live. | M19 p2 |
| The batched review (id 5198312441, `COMMENTED`, 13:33:07Z) put the same `created_at` and `pull_request_review_id` on all five inline comments (ids 4005702541–571). `reviewDecision` stayed `""` — a `COMMENTED` review is not a decision. | `gh api …/pulls/15/comments`; `gh pr view --json reviewDecision`. | M19 p2, M20 p2 |
| `gh pr view --json reviewDecision` prints `""` where GraphQL returns `null`. | Both queried at 13:33Z. | M20 p1 |
| Review threads exist only in GraphQL (`reviewThreads`, ids `PRRT_…`). After the author's push (`0c5a18d`, 13:41:11Z) **all five threads read `isOutdated: true`**, and `line` went `null` on the four RIGHT-side threads while the LEFT-side one kept `line: 15` (a deleted line is a fact about the base). Outdated ≠ resolved. | Two queries, 13:33:29Z and 13:41:34Z. | M20 p1, M23 p1 |
| `resolveReviewThread` works for the author; `resolvedBy` records the login. **Resolution leaves no REST timeline event** — `/issues/15/timeline` shows `committed`, `connected`, `commented`, `reviewed` only. | Five mutations 13:42:07–13Z; REST timeline. | M20 p1 |
| Each reply via `POST …/pulls/15/comments/{id}/replies` carries `in_reply_to_id` **and is recorded as a `COMMENTED` review** in `--json reviews` (five extra reviews at 13:42:00–07Z). `latestReviews` keeps one entry per reviewer and **omits the PR author entirely** — it listed only the bot. The GraphQL timeline with `PULL_REQUEST_REVIEW` items did not list these reply pseudo-reviews. | `gh pr view 15 --json reviews,latestReviews`; GraphQL timeline. | M20 p2, M23 p1 |
| **`reviewDecision` did not move** through the push, five replies, and five resolutions: `CHANGES_REQUESTED` from 13:34:14Z onward. Only a review with a verdict moves it. | Read at 13:41:14Z, 13:45:12Z, 13:47Z. | M20 p2 |
| `gh pr view --comments` labels review summaries `status: commented` / `changes requested` and Conversation comments `status: none`, interleaved. | Live. | M20 p2 |
| `gh issue view --comments` and `--json` are mutually exclusive: `specify only one of --comments or --json`. | Live (while fetching #14 for `/code-review`). | M24 p2 |

#### The second identity

| Fact | Evidence | Page |
|---|---|---|
| A `workflow_dispatch` workflow (`.github/workflows/review-bot.yml`, left on w3probe `main` at `bba30dd`) running `gh pr review` with `GITHUB_TOKEN` **can `--request-changes`**: review by `github-actions[bot]` at 13:34:14Z; `reviewDecision` `""` → `CHANGES_REQUESTED`. | Run 34850034617. | M20 p1/p2 |
| **It cannot approve by default**: `failed to create review: GraphQL: GitHub Actions is not permitted to approve pull requests. (addPullRequestReview)`. `GET repos/…/actions/permissions/workflow` and `GET orgs/perro-ruidoso/actions/permissions/workflow` both return `{"default_workflow_permissions":"read","can_approve_pull_request_reviews":false}`. **Flipping it is a permission grant; the auto-mode classifier refused the `PUT` in this session and it was left alone.** | Run 34850913901, 13:42:40Z. | M20 p1 |
| **A bot cannot be a requested reviewer**: `gh pr edit 15 --add-reviewer "github-actions[bot]"` → `GraphQL: Could not resolve user with login 'github-actions[bot]'. (requestReviewsByLogin)`; REST `POST …/requested_reviewers -f "reviewers[]=github-actions[bot]"` → 201 with `requested_reviewers: []`. | Live, 13:35:00Z. | M20 p1, M23 p2 |
| Therefore PR #15 has **no `review_requested` event and no `APPROVED`**, and cannot with one human. The transitions are shown read-only on **`cli/cli#14136`** ("Add worktree checkout to `gh issue develop`", author sergiou87): `CHANGES_REQUESTED` by babakks 2026-08-18T11:46:11Z → commits by tidy-dev 08-20T15:35:03Z → `review_requested babakks by tidy-dev` 08-20T17:31:39Z → commits 17:31:57Z, 08-21T14:19:44Z → `APPROVED` by babakks 08-21T14:36:57Z → merged 15:11:54Z; `reviewDecision` now `APPROVED`. Three of its `review_requested` events have a non-User `requestedReviewer` (Copilot) and print as `null` under a `... on User` fragment. | GraphQL `timelineItems` with `REVIEW_REQUESTED_EVENT, PULL_REQUEST_REVIEW, PULL_REQUEST_COMMIT, MERGED_EVENT`. | M20 p2, M23 p2 |
| Of 100 recent merged `cli/cli` PRs, **4** carried a `CHANGES_REQUESTED` review (#14278, #14198, #14178, #14136). | `gh pr list --state merged --limit 100 --json reviews`. | — |
| **Consequence for the course:** A4 is paired; the student opens the drill PR on their own Instance so they are its author and the peer can give a verdict; the guide answers the second-identity question ("the peer, and only the peer") and says what a stand-in costs. | — | A4, guide Part 10 item 7 |

#### `/code-review` (M21)

| Fact | Evidence | Page |
|---|---|---|
| Invoked as the installed Pocock skill on the planted branch, fixed point `main` (`bba30dd`), merge base `309b051`, one commit, 2 files. Spec source found at step 2's first rung (`Closes #14` in the commit → `gh issue view 14`); standards sources `CLAUDE.md`, `CONTEXT.md`, `docs/adr/0001…`, `docs/agents/domain.md`. Two `general-purpose` sub-agents in parallel: Standards 64 s / 3 tool uses, Spec 56 s / 3 tool uses. | Session. | M21 p1 |
| **Both axes found all three planted bugs and invented no bug.** Standards: 6 hard findings (failure reset; floor order; `round()`; stale docstring; "PR must name the ADR rule — the commit message names none; if the PR body matches, that's a breach" + `domain.md`'s flag-ADR-conflicts rule; the floor test's name) + 3 smells (Mysterious Name `ef`/`reps`/bare literals; "Primitive Obsession (magic literals)" on the nested conditional; "Speculative Generality (inverse)" on the no-op clamp). Spec: 3 wrong-implementation, 1 missing (tests no longer pin every rule), 1 scope creep, verdict "does not satisfy #14". Kept **verbatim** in `code-review-output.md` and on M21 p2 (including the agent's literal `&lt;`). | Sub-agent returns. | M21 p2 |
| **Verified before judging:** the three behavioural claims hold (grade 3 from 1.3 raises `Card.ease_factor must be at least 1.3`; 5×2.5 → 12; fail from 2.36 → 2.5). The Spec agent's "Running the pre-change main tests against the new code fails 5 of them" is **4** once the removed `round_half_up` import is stubbed (the file does not import at all otherwise). | `pytest` on `main`'s test file against the planted code. | M21 p3 |
| Verdicts: 4 must-fix (bugs 1–3 + the test rewrite), 4 nits (docstring; `domain.md` process rule; naming; the mislabelled smell), **1 false positive** (the CLAUDE.md "must name the ADR rule" finding — the rule binds the PR description, and PR #15's body names Ease Factor, Failure, and Rounding; the agent read the commit and hedged), 1 duplicate (the clamp smell = bug 1), 2 non-findings. | Reading against the sources. | M21 p3 |
| `docs/agents/domain.md` does contain "## Flag ADR conflicts — If your output contradicts an existing ADR, surface it explicitly rather than silently overriding" — the Standards agent's citation was accurate. | File. | M21 p3 |

#### The author's turn (M23) and `/qa` (M24)

| Fact | Evidence | Page |
|---|---|---|
| Fix commit `0c5a18d` (13:41:11Z): the three rules restored in the one-function shape, `main`'s tests restored under their names (the two `round_half_up` unit tests became one through `review()`); **49 passed**, ruff/format/mypy clean; commit message names each ADR rule and the thread it answers. | `git log -1`; checks. | M23 p1 |
| The prompt on M23 p1 is the direction recorded for the drill; on the throwaway the direction came from the build session, and the page says so. | — | M23 p1 |
| `/qa` (installed) was given a two-part report in one message; **no clarifying question** was needed; an `Explore` sub-agent (96 s, 13 tool uses) returned the `CONTEXT.md` vocabulary, the `list` command's documented contract (exit 1 "if the deck could not be read"), that per-card error indexes are **zero-based** ("card 1" is the second card), that no test covers a below-floor EF in a deck file, and the ADR sentence verbatim. Scope: report 1 split into two thin issues; report 2 single. | Session. | M24 p1 |
| Filed **#16** (a deck with one invalid card cannot be listed), **#17** (errors name a card by zero-based position), **#18** (ADR 0001 misstates SuperMemo on rounding) at 13:48:35/40/44Z with `gh issue create --body-file`. **No labels, no type** — the skill's text says `gh issue create` and nothing else; `triage-labels.md` is `/triage`'s. Bodies carry `\r\n` (written on Windows); GitHub renders them fine, but jq's `scan("^## .*"; "m")` returned one heading swallowing the body — `split("\n")[] | select(startswith("## ")) | rtrimstr("\r")` works. | `gh issue view 17 --json …`. | M24 p2 |
| PR #15 unchanged after `/qa`: 2 files, commits `b0fac63 0c5a18d`, `closingIssuesReferences` → #14 only. | `gh pr view 15`. | M24 p1 |
| Probe behind #16/#17: `flashcards list --deck bad.json` with one card at EF 1.2 prints `flashcards: ..\bad-deck.json: card 1: Card.ease_factor must be at least 1.3`, exit 1, no traceback, no other cards shown. | Local run. | M24 p1 |

#### Decisions taken in this unit

- **`seed/SPEC.md` §10 — prepared PR versus patch: prepared PR, opened by the student from
  course-supplied files.** `seed/planted/` (`scheduler.py` with its own `ReviewState` so it
  depends only on the template's ADR, not on T01; `test_scheduler.py`; `ticket.md`; `pr-body.md`)
  and `seed/tools/plant_review_pr.py` (files the ticket, `gh issue develop`, copies, commits,
  pushes, opens the PR with `Closes #N`; refuses if `scheduler.py` exists). Reasons in §10.
  **Tested live** on `flashcards-w2probe` (fresh-template Instance, no T01): issue #10, branch
  `10-sm2-scheduler`, PR #11 authored by the runner, `closes [10]`, 2 files, **CI green with the
  three bugs in**. Refusal path tested on w3probe. The earlier note that the diff "can only be
  built on top of an Instance where T03 has landed" was true of the Card-based version only.
- **S3 (M24's skill): keep `/qa`, vendored.** `skills/qa/SKILL.md` + `skills/README.md` (origin,
  MIT, one-`curl` install). `/triage` and `/to-tickets` do different jobs. Objective row's
  primary source now says "vendored by the course - removed upstream 2026-08-05".
- **Stack on the audit branch, not `17-week3-pages`** (above).
- **Not decided here:** S1 (pin vs track the plugin) and S2 (`request-refactor-plan` in M18);
  the `can_approve_pull_request_reviews` flip (not needed — A4 pairs students).

#### Checkers and site

- `checkers/check_a4.py` (new; two handles, `--pairs FILE` runs both directions) grades: Instance
  exists; a drill PR touching `src/flashcards/domain/scheduler.py` (light `gh pr list` then
  `gh pr view` — the full field set on 100 PRs exceeds GitHub's GraphQL node limit, "requesting
  up to 1,000,000 possible nodes which exceeds the maximum limit of 500,000"); authored by the
  student; a peer review with a verdict; ≥ 2 inline comments by the peer; a ```suggestion block;
  ≥ 1 resolved thread; a commit after the verdict; a `ReviewRequestedEvent` for the peer after
  the last commit; peer re-review (note); issues with `/qa`'s headings created after the PR
  opened (labels/type as a note); file set ⊆ the drill's two; PR not closing the `/qa` issues;
  `a4-writeup.md` (≥ 300 words, `## Standards` + `## Spec`, the three verdict words). Against
  w3probe with `--peer github-actions` it fails author, inline, suggestion, re-request, write-up;
  with `--peer acatlin` it fails author, verdict, follow-up, re-request, write-up — **one identity
  cannot pass it, which is the point**. Nonexistent handle stops at *Instance exists*.
  **Fault-injected 16/16 by snapshot replay** (`fault_a4.py` in the scratchpad: 9 recorded `gh`
  calls; a synthetic positive control that passes all 18 checks; one mutation per rule).
  Cascades are expected (no verdict → no follow-up → no re-request; no inline → no suggestion).
- `checkers/check_site.py`: **new rule from a real defect** — a stray `</tt>` shipped in M24 p2
  and nothing caught it; the checker now runs `html.parser` with a tag stack and reports a
  closing tag that does not match the innermost open element, and any element left open. Verified
  by injection on a scratch copy (stray `</tt>`, unclosed `<div>`) alongside five existing rules
  (hub link, Apply checklist, duplicate deck id, escaping link) — 6/6 caught. **56 pages, 587
  internal links, clean.**
- `objectives/build_objectives.py`: 14 pages for M19–M24 (51 pages across 24 objectives).
- Self-checks: 40 questions on 14 pages; **35 flagged** on the first option-form scan (all
  "longest"; two also "only-code"), rebalanced in four passes to **0 flagged**; letters
  12/10/7/11.
- Render: extension not connected; headless Chrome (`--headless=new --virtual-time-budget`)
  from a same-origin iframe harness at 1200 and 400 px: 13 decks / 104 cards run to "Deck
  complete" with the list hidden and a `localStorage` record, 40/40 self-checks wrong-then-right
  with first-try tally 0/N, no Mermaid on this week, **no overflow at either width**, zero
  `CONSOLE` lines on the stderr channel (a probe page confirmed the channel catches
  `console.error` and an uncaught `ReferenceError`). One page screenshotted at 1200 px and read.
  Harness deleted before commit.

**Left over for the instructor:** `flashcards-w3probe` now also holds #12–#18, PRs #13 (merged)
and #15 (open, `CHANGES_REQUESTED`, five resolved threads), the `review-bot.yml` workflow, and
branches `12-sm2-scheduler`, `14-simplify-scheduler`; `flashcards-w2probe` holds #10 and PR #11
(open). Both still on the delete list (`delete_repo` scope). Nothing on the pages depends on
either surviving. Not done: the Seed's ADR 0001 rounding-source sentence (w3probe#18 says what
to change — suggest a one-line fix in the Seed before cohort 1); S1/S2; the
`can_approve_pull_request_reviews` flip (not needed).

## How to build the remaining weeks (preference recorded 2026-09-14)

Weeks 1–4 were each one long session; the instructor's context window is the limiting
resource. From Week 5 on, build a week in **six short sessions on one `gh issue develop`
branch**, each ending in a commit and a NOTES.md update so the next session starts cold from
this file: (1) sources + the whole throwaway run in one go — the exhibit's timestamps must be one
story — recording every command and output in the week's NOTES section as it happens; (2–4)
pages, two objectives per session, `check_site.py` and the option-form scan on those pages
only, a hub stub first; (5) assignment + checker + fault injection; (6) hub, Course Home,
pager, objectives, README/roadmap/guide, render at both widths, PR. Each prompt opens with
"read NOTES.md's Week N section; do not re-run anything on the throwaway." Do not split the
throwaway run or the final whole-week render pass.

## Open questions

- ~~Linear Free plan's Issues Sync availability~~ — **resolved 2026-09-13**, twice: the
  morning reading of the pricing page, then a cell-level parse of the table before M12 was
  written (above). M12 is written for Free. Still owed: one live walk of the M12 protocol
  in the instructor's Free workspace, with dated captures.
- **The Seed Repo's tickets have no labels, no type, and no parent.** M08 uses that as an
  exhibit of what an unclassified backlog costs. Whether to label and type them (`layer:*`,
  `Task`) is the instructor's call; doing so would make `flashcards-seed` a better M08
  exhibit and a worse one for the point M08 currently makes. Not done in this unit.
- ~~**`gh` minimum version is now 2.94.0** for Week 2. `instructors/student-setup.md` and the
  guide's toolchain section predate this and should say so before the cohort installs.~~ —
  **closed 2026-09-13:** the handout asks for 2.94.0+, the guide's reference state is 2.100.0,
  and the teaching machine is on 2.100.0.
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
- **Linear branch-name linking, live.** M13 page 2 quotes Linear's rule and marks it as not
  observed. Do it with the Issues Sync live check (same workspace, five minutes).
- **`request-refactor-plan` is gone upstream** (2026-08-05). M18 names it because the
  objective does; the page quotes the installed copy and says it was removed. Decide before
  cohort 2 whether to keep it in M18 or swap in a surviving skill. **Sharpened 2026-09-14:**
  the changeset that removed it names its replacement — `/to-spec` and
  `/improve-codebase-architecture` — and the plugin students install never contained it, so
  "keep it" means shipping a copy the course maintains. Recommendation: swap in
  `improve-codebase-architecture` (Weeks 1–3 audit, S2).
- **The plugin and the course machine run different skills** (found 2026-09-14). The
  handout installs the Claude Code plugin (25 skills, tracking upstream); the course machine
  has a 2026-07-09 `npx skills` snapshot (38). The plugin lacks `request-refactor-plan`, `qa`,
  `git-guardrails-claude-code`, and `claude-handoff`; its `ask-matt` gives the opposite
  advice about `/handoff` versus `/compact` and a different smart-zone figure. Decide whether
  the course pins a skill set or tracks the plugin (Weeks 1–3 audit, S1); until then the M18
  pages quote both and A3's third situation was rewritten to hold under either. **Week 4
  (2026-09-14) narrowed it:** `code-review` is in the plugin and differs from the installed copy
  only in punctuation, so M21 holds under either; `qa` is vendored (above). What S1 still
  decides is M18's two absent skills and `ask-matt`'s reversed advice.
- ~~**M24 names `/qa`, which upstream retired on 2026-08-05** into `/triage` and `/to-tickets`.
  Week 4 is unbuilt; decide the skill before it is (Weeks 1–3 audit, S3).~~ — **decided
  2026-09-14, building Week 4: keep `/qa`, vendored** at `skills/qa/SKILL.md` (MIT, byte-identical
  to the last upstream copy). The named replacements do other jobs: `/triage` moves existing
  issues through states, `/to-tickets` decomposes a spec; neither files an issue from a
  conversation, which is what M24 assesses. Re-check upstream before each cohort.
- **The Seed's ADR 0001 misstates its source on rounding** (found 2026-09-14). It says the
  SM-2 publication "does not settle" rounding; the cited page says "If interval is a fraction,
  round it up to the nearest integer." The ADR's half-up rule stands; the sentence about the
  source should say the course deliberately departs from it and why. Filed on the throwaway as
  w3probe#18 by `/qa`; a one-line fix in `flashcards-seed` is owed before cohort 1.
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
  M16 move, done on the course repo first. Opening it showed that a stacked PR's `Closes`
  keyword is ignored until the base is the default branch (verified above); re-check
  `closingIssuesReferences` on #14 after retargeting.
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

- **2026-09-13** — **Week 1–2 audit** (issue #15, branch `15-audit-weeks-1-2`), run with
  the tools live on the newly installed `gh` 2.100.0. Findings, evidence, and fixes are in
  the "Week 1–2 audit" section above, step by step. Headlines: `cli/cli#14398` closed
  unmerged the same morning and four pages were re-captured around it; M06's course-repo
  snapshot was two PRs and one dependency edge stale and its "no other issue has a blocker"
  sentence had become false; #14's retarget-then-close record (15:40:05 / 15:43:30 /
  15:43:31) is now M06's second worked example; one GitHub Docs sentence quoted on M11 had
  been rewritten upstream; three Week 3–5 `RESOURCES.md` URLs had moved; `check_site.py`
  accepted an empty flashcard face (fixed, 25/25 faults now caught); seven pages overflowed
  at 400 px because of unbreakable `--jq` tokens in `.code-label` (fixed in CSS); and 81 of
  93 self-check questions gave the answer away by option length (all rewritten, 0 flagged).
  Not done: deleting `flashcards-w2probe` (no `delete_repo` scope; command in Part 10) and
  the Linear live walk, unchanged.

- **2026-09-13** — **Week 3 built** (M13–M18): the hub, fourteen Learning Pages (two per
  objective, three for M16), `assignments/a3.md` with its rubric, and `checkers/check_a3.py`.
  Filed as **#17**, blocked by #13 (Week 2); branch `17-week3-pages` made with `gh issue develop 17
  --base 15-audit-weeks-1-2`; **PR #18 stacked on the audit branch** (#16 was still open and the
  pages need its checker and CSS fixes) — retarget to `main` after #16 merges, at which point
  `Closes #17` takes effect; it read `closes: []` at creation, as M16 page 2 predicts. Every command on
  every page was run on a throwaway Instance the same day — the week was *done*, not described:
  three tickets with edges, `gh issue develop` for each branch, a stacked PR, its retarget after
  a squash merge and the rebase that followed, a deliberately authored drive-by PR closed and
  split, a genuine conflict resolved by invoking `/resolving-merge-conflicts` in Claude Code,
  and two probes of what deleting a merged parent branch does to the child. Findings are in the
  "Week 3" section above; the ones that changed what the pages teach:
  - `Closes #n` on a stacked PR is ignored until the base is the default branch (the 2026-09-13
    #14 finding, now shown with `connected` timestamps), and `closingIssuesReferences` is empty
    for a second or two even on a `main`-based PR — read twice.
  - A squash-merged parent makes the retargeted child's diff grow; `git rebase origin/main`
    prints "skipped previously applied commit" and fixes it. The course repo's #14 did exactly
    this (force-push at 15:42:45), which M06 had not previously explained.
  - `gh pr merge --delete-branch` on a parent **closes** the stacked child; only GitHub's own
    auto-deletion retargets it. The docs describe the second; a student following the CLI
    example on the same page would hit the first.
  - `mergeable` reads `UNKNOWN` for ~30 s after a sibling merges before it reads `CONFLICTING`.
  - `request-refactor-plan` was removed upstream on 2026-08-05; the installed skills are a
    2026-07-09 snapshot.
  - M14 has no primary source; Google's eng-practices "Small CLs" is quoted as ancillary and
    marked so on the page, with a new `.tier.anc` chip.
  - `check_a3.py` grades evidence only and was fault-injected 13/13 against a recorded
    snapshot; `check_site.py` now requires a checklist on Evaluate pages; the site is 42 pages,
    462 links, clean; 40 new self-check questions, 0 flagged by the option-form scan; render
    verified in headless Chrome at 1200 and 400 px (the extension was not connected).
  - Left over: delete `flashcards-w3probe` (with `w2probe`); the Linear branch-name link is
    documentary; two branch-deletion paths untested; the `request-refactor-plan` decision.

- **2026-09-14** — **Weeks 1–3 audit** (issue #19, branch `19-audit-weeks-1-3` from
  `17-week3-pages` via `gh issue develop`; **PR #20**, opened 13:00:50Z with base
  `17-week3-pages` — picked by `gh pr create` from `gh-merge-base` — and
  `closingIssuesReferences: []` on creation, stacked on #18, which is stacked on #16; #16 had
  not merged, so the #18 retarget the brief asked for could not be recorded; the *before* state
  is on M06 p3 and M16 p2 instead, and this three-deep stack is the next exhibit to record
  when it unwinds). Findings, evidence, and fixes are in the
  "Weeks 1–3 audit" section above. Headlines: all 105 URLs 200 with no redirects; every
  quotation present, four course-artifact quotations tidied (an elision, a truncation, an
  "opens", a code block rendered as a sentence) and one Anthropic sentence extended
  upstream; **the skills drift is far larger than the 13th recorded** — `qa` was retired with
  `request-refactor-plan` and the changeset names both replacements, the plugin students
  install has 25 skills and lacks two of M18's six, `ask-matt` reversed its `/handoff`
  advice and moved the smart zone to ~150k, `grilling` was rewritten, `wayfinder` says
  "decision tickets"; `cli/cli`'s listings moved again and M06's course-repo snapshot was a
  day stale (four edges now, three open issues, a second stack in its *before* state);
  **nine links to files outside `docs/` were 404 on the published site** (fixed, and
  `check_site.py` now refuses them — 28/28 faults caught); `check_a3.py` 16/16 by snapshot
  replay, `check_a1/a2` 22/22 by live mutation on w2probe (a deleted-and-recreated label
  does not re-attach to issues); 42 pages render clean at both widths (10 diagrams, 38 decks,
  133 self-checks, 0 flagged, A–D 36/33/29/35); cross-week pass found one contradiction
  (M01 p2 said the backlog is inherited), one term used before definition ("frontier"), a
  one-second/two-second mismatch, a four-flags/six-flags mismatch, and the guide's stale
  `gh` minimum and scope lines. Nine suggestions recorded, three needing decisions (pin or
  track the plugin; swap `request-refactor-plan`; name M24's skill). Not done: deleting the
  throwaways (no `delete_repo`; ask first), the Linear live walk, the #18 retarget.

- **2026-09-14** — **Week 4 built** (M19–M24): the hub, fourteen Learning Pages (two per
  objective, three for M21), `assignments/a4.md` (paired) with its rubric, `checkers/check_a4.py`
  (two handles), the planted-bug package `seed/planted/` + `seed/tools/plant_review_pr.py`, and
  the vendored `skills/qa/`. Filed as **#21** (blocked by #17 and #19); branch `21-week4-pages`
  from `19-audit-weeks-1-3` via `gh issue develop`; **PR #22** opened 14:51:54Z with base
  `19-audit-weeks-1-3` (picked by `gh pr create` from `gh-merge-base`) and
  `closingIssuesReferences: []`, as M15 p2 predicts — a **four-deep stack** (#16 ← #18 ← #20 ←
  #22), stacked on the audit rather than on `17-week3-pages` because the audit's checker rule
  and NOTES/guide edits are what this unit extends. Every transcript is from one PR on the Week 3
  throwaway (`flashcards-w3probe#15`): T03 landed correctly (#12/#13), then a "refactor" that
  planted the three §7 bugs with a green suite; a Conversation comment; a batched review from
  `gh api` with five inline comments and a suggestion (two 422s quoted); the author's own
  `APPROVE`/`REQUEST_CHANGES` refused by both routes (quoted); a `workflow_dispatch` bot that
  could request changes but was refused approval and cannot be a requested reviewer; the
  installed `/code-review` with both sub-agent reports kept verbatim and every finding given a
  verdict (all three planted bugs found; one false positive, one mislabelled smell, one wrong
  count — "5" was 4); the fix through Claude Code with a reply per thread and five threads
  resolved by GraphQL while `reviewDecision` stayed `CHANGES_REQUESTED`; `/qa` filing three
  unlabelled, untyped issues with the PR untouched. Findings are in the "Week 4" section above;
  the ones that changed what the pages teach:
  - An author cannot review their own PR with a verdict, cannot request a review from
    themself (silent no-op), and a bot cannot be requested at all — so the second identity is
    the peer, A4 is paired, and the student opens the drill PR on their own Instance.
  - A push, replies, and resolutions do not move `reviewDecision`; each reply is recorded as a
    `COMMENTED` review; `latestReviews` omits the author; resolution leaves no timeline event.
  - There are two `/code-review`s — Claude Code's built-in and the Pocock skill — and the
    course's is the one with `## Standards` / `## Spec`.
  - `/qa` applies no labels and no type; the checker notes them.
  - The SuperMemo page says "round it up"; the Seed's ADR says the original leaves rounding
    open — filed, not fixed.
  - `seed/SPEC.md` §10 settled: prepared PR, opened by the student (planting script tested
    live on `flashcards-w2probe`: issue #10, PR #11, CI green with the bugs in).
  - `check_a4.py` fault-injected 16/16 by snapshot replay; `check_site.py` gained a
    mismatched-tag rule from a real stray `</tt>` (6/6 injected faults caught); 56 pages, 587
    links, clean; 40 self-check questions, 35 flagged on the first scan → 0; 14 pages
    render-tested headless at 1200 and 400 px, no overflow, no console output.
  - Left over: both throwaways (now with Week 4 artifacts; `delete_repo` scope still missing);
    the Seed ADR sentence; S1/S2; three course-repo blob links on the pages that 404 until this
    PR merges (`skills/qa/SKILL.md`, `skills/README.md`, `assignments/a4.md`).
