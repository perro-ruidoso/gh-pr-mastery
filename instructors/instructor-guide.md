# Instructor Guide — GitHub Pull Requests for Agentic Coders

**Audience:** the person teaching this course. It assumes you can program, read a
terminal, and use `git` for ordinary work — and it assumes **nothing** about GitHub
organization administration, Claude Code skills, or Linear. Where those three are
involved, every step is spelled out.

**Scope:** everything you need to stand the course up and teach **Week 1** (M01–M06,
assignment A1). Weeks 2–6 do not exist yet; see `roadmap/roadmap.docx`.

---

## How to read the commands in this guide

| Marker | Meaning |
|---|---|
| **[run 2026-09-12]** | This exact command was executed against the real org/repos on that date, and the output shown is what it printed. |
| **[untested]** | Correct per vendor documentation, but not executed here. Check it the first time you run it, and fix this file if it is wrong. |
| *(no marker)* | Ordinary local command with no course-specific risk (`git`, `pip`, `python`). |

This convention matters because the whole repo is built on it: `NOTES.md` records what
was verified and when, and the vendor-behaviour facts move. **Re-verify before each
cohort.** That is not boilerplate — two of `NOTES.md`'s facts overturned a design
decision the week the course was built.

Shell: transcripts use **bash** (macOS, Linux, Git Bash on Windows). Where PowerShell
differs in a way that will actually bite, both are given. Students are the same.

---

## Part 0 — Before you do anything

### 0.1 The shape of the thing

Six weeks, ~4 hrs/week of student time, cohort of 8–14, one live meeting per week,
36 mastery objectives. **The subject is the workflow, not the application.** Students
direct Claude Code to write Python; they are graded on issues, dependency structure,
branches, diffs, review, gates, and the PM layer — never on the Python.

Read `MISSION.md` (5 min) and `CONTEXT.md` (10 min) before your first meeting.
`CONTEXT.md` is the ubiquitous language: use its words in class and students inherit
precision for free. The two that earn their keep in Week 1 are **Instance** (a student's
own copy of the Seed Repo) and the course repo read as an **exhibit**.

### 0.2 Three repos, and never confusing them

| Repo | What it is | Who writes to it |
|---|---|---|
| `perro-ruidoso/gh-pr-mastery` | **Course Repo.** These pages, the objectives, the checkers. Also a Week 1 teaching exhibit, because it is built with the workflow it teaches. | You only. |
| `perro-ruidoso/flashcards-seed` | **Seed Repo.** A template repository holding a Python flashcard CLI, CI, and a 15-issue backlog with real blocking edges. | You only, and rarely. |
| `flashcards-<handle>` | A student's **Instance** — their own copy of the Seed Repo, created from the template in Week 1 and worked in for six weeks. | That student. |

A fourth, `flashcards-upstream`, appears in Week 5 and **does not exist yet**. Do not
mention it beyond "later" in Week 1; the M01 page already handles it.

M01's page calls conflating these "the single most common Week 1 mistake." Believe it.

### 0.3 Four decisions you owe before students arrive

These are open in `NOTES.md` and `roadmap/roadmap.docx`. Two of them block Week 1.

**(a) Org plan: pay for Team seats, or downgrade to Free? — blocks inviting students.**
The org is on GitHub Team with 2 seats, 1 filled **[run 2026-09-12]**:

```bash
$ gh api orgs/perro-ruidoso --jq '{login,plan:.plan.name,seats:.plan.seats,filled:.plan.filled_seats}'
{"filled":1,"login":"perro-ruidoso","plan":"team","seats":2}
```

A cohort of 8–14 plus you needs 9–15 seats at $4/user/month. **Recommendation: downgrade
to Free before inviting.** `adr/0003` establishes that downgrading costs the curriculum
nothing — every gate the course actually uses (rulesets, required checks, required
reviews, conversation resolution, merge queue) works on a **public** repository at either
tier, and all course repos are public by requirement. If you would rather not touch
billing mid-build, staying on Team is harmless except to your wallet; nothing in the
curriculum depends on it either way. What you must not do is leave the org at 2 seats and
discover it while inviting fourteen people.

**(b) The fifth triage label is free — affects A1 grading, not the mechanics.**
A1 item 4 asks students to create five triage labels, but `wontfix` is in GitHub's
default label set and arrives on **every** new repository, template-derived or not. This
was established by experiment, not assumed **[run 2026-09-12]**:

```bash
$ gh label list --repo perro-ruidoso/flashcards-seed --json name --jq '[.[].name]|join(", ")'
accessibility, bug, documentation, duplicate, enhancement, good first issue, help wanted, invalid, question, wontfix
```

So the item genuinely assesses **four** labels. No change to the template can fix it.
Three options, from `NOTES.md`: accept it; rename the fifth role to something outside the
defaults (`declined`), which costs a change to the Pocock skill's own vocabulary; or make
`check_a1.py` assert `wontfix` was *edited* (colour or description changed from GitHub's
default) as evidence of deliberate handling. **Recommendation for cohort 1: accept it,
and say so out loud in class.** It is a live example of a spec meeting a platform default
— exactly the kind of thing this course trains people to notice. Changing the shared label
vocabulary to win one rubric point is not worth the blast radius.

**(c) Does Linear's Free plan include GitHub Issues Sync? — blocks Week 2 (M12), not
Week 1.** Unresolved. See Part 5. You have until Week 2 to answer it; do it during Week 1
so it is never urgent.

**(d) Can your Claude Pro subscription absorb the cohort's CI review volume, or do you
need Max?** A Week 5 question, measured during the Week 5 dry run. Ignore it for now.

### 0.4 Time budget for standing the course up

| Task | Realistic time |
|---|---|
| Your machine (Part 2) | 30–45 min |
| Org setup and invitations (Part 3) | 30 min, plus waiting on students |
| Verifying the infrastructure end to end (Part 4) | 45 min — **do not skip this** |
| Linear (Part 5) | 45 min, most of it resolving decision (c) |
| Preparing the Week 1 session (Part 7) | 2 hrs the first time |
| Grading A1 for 12 students (Part 8) | ~15 min of script + ~10 min per write-up |

---

## Part 1 — Vocabulary you need and probably don't have

Skim this if you have never administered a GitHub org or run Claude Code skills. Every
term here appears in a step later.

**Organization.** A shared namespace owning repositories, with members, teams, and
roles. The roles that matter: **owner** (full admin — you) and **member** (default —
students). Distinct from repository **collaborator**, which is granted per-repo.

**Membership visibility.** Whether the world can see that you belong to an org.
**Private by default.** The course requires **public** for every student, because tools
that ask "does this person have write access via the org?" — including the Claude GitHub
App in Week 5 — cannot see a private membership and will refuse to act. This is the
highest-value two-minute step in Week 1.

**Token scope.** A permission attached to your `gh` token, saying what the token may ask
for. Distinct from a repository **permission**, which says what your *account* is allowed
to do. Students get this backwards; A1's self-check question 4 exists for exactly that
reason. Add a scope without re-logging in:

```bash
gh auth refresh -s <scope>
```

**Template repository.** A repo flagged so others can create fresh copies of its files.
A copy **starts with a single commit** and has no ongoing link to the original. Contrast
a **fork**, which carries the entire commit history and stays linked to its parent — which
is what makes cross-repo PRs possible (Week 6). Week 1 uses a template, Week 6 uses a
fork, and the contrast is taught deliberately.

**Skill.** A packaged set of instructions Claude Code loads when a task matches it,
invoked as a slash command (`/to-spec`, `/code-review`, `/triage`). This course uses a
family of them from `mattpocock/skills`. They are **installed once per machine** and
**configured once per repository** — two different things students will conflate.

**`docs/agents/`.** The per-repo configuration those skills read: where issues live, what
the triage labels are called, where domain docs are. Written by
`/setup-matt-pocock-skills`. Deliberately **absent from the Seed Repo** — producing it is
what A1 item 3 grades. If you ever find yourself "helpfully" adding it to the template,
you have just deleted an objective.

**Issue Dependency vs. Sub-Issue.** Two different GitHub features, and the difference is
load-bearing here. An Issue Dependency is a **graph** — an issue can be blocked by many
and block many. A Sub-Issue is a **hierarchy** — one parent, up to eight levels deep. Five
of the Seed Repo's fifteen tickets have *two* blockers, which a hierarchy structurally
cannot express. Week 1 asks students only to *read* a dependency; Week 2 (M11) assesses
the distinction. There is no `gh issue edit` flag for dependencies as of `gh` 2.92.0 —
they are reached through `gh api`, and the payload takes the blocker's **database id**,
not its issue number.

---

## Part 2 — Your machine

Do this yourself before you ask students to. You will be debugging their version of it
live in the first session, and the fastest way to be useful is to have hit the problems
first.

### 2.1 Install

| Tool | Minimum | Check |
|---|---|---|
| `git` | 2.30+ | `git --version` |
| Python | 3.10+ (the Seed Repo's CI pins 3.12) | `python --version` |
| GitHub CLI (`gh`) | 2.60+ | `gh --version` |
| Claude Code | current | `claude --version` |

Reference state on the build machine **[run 2026-09-12]**: `gh` 2.92.0, Python 3.14.4,
git 2.52.0.windows.1, Claude Code 2.1.269.

```bash
# macOS
brew install git gh python@3.12
npm install -g @anthropic-ai/claude-code
```

```powershell
# Windows (PowerShell)
winget install --id Git.Git
winget install --id GitHub.cli
winget install --id Python.Python.3.12
npm install -g @anthropic-ai/claude-code
```

Claude Code needs a **Claude Pro subscription** (about $20/month) — yours, and each
student's. It is stated as a course requirement on Course Home and must be in the syllabus
before enrolment.

### 2.2 Authenticate `gh`

```bash
gh auth login          # GitHub.com -> HTTPS -> authenticate in browser
gh auth status
```

Read the **token scopes** line, which is the part people skip. Yours, as the instructor
**[run 2026-09-12]**:

```
github.com
  ✓ Logged in to github.com account acatlin (keyring)
  - Active account: true
  - Git operations protocol: https
  - Token: gho_************************************
  - Token scopes: 'admin:org', 'gist', 'project', 'repo', 'workflow'
```

**Students need:** `repo`, `read:org`, `gist`, `workflow` — enough for everything through
Week 4.

**You additionally need `admin:org`**, to invite members and manage teams:

```bash
gh auth refresh -s admin:org
```

And once, to remove throwaway repositories from smoke-testing the template (Part 4.4),
you need `delete_repo`. It is deliberately not in the default set:

```bash
gh auth refresh -s delete_repo
```

### 2.3 Install the engineering skills

The course's workflow spine (`/to-spec`, `/to-tickets`, `/implement`, `/code-review`,
`/qa`, `/triage`, and the Week 1 one, `/setup-matt-pocock-skills`) comes from
`mattpocock/skills`. **There are two install routes, and installing both leaves you with
every skill twice** — the upstream README says so explicitly. Pick one.

**Route A — Claude Code plugin (recommended for a cohort).** A managed, read-only bundle
that updates when upstream ships. Inside Claude Code:

```
/plugin install mattpocock-skills
```

It is in Claude Code's official marketplace, so there is nothing to add first. This is the
route to put in the student handout: one line, nothing to maintain, everyone on the same
version.

**Route B — copy editable files into your project.**

```bash
npx skills@latest add mattpocock/skills
```

This writes the skills into the repo as ordinary files you own and can edit; nothing
updates behind your back. Choose this only if you intend to modify a skill — for example,
if you take option (b) on decision 0.3 and rename the fifth triage label. If you do,
**make sure `setup-matt-pocock-skills` is among the skills you select**; the installer
lets you pick, and A1 fails without it.

Verify either way by starting `claude` in any repo and typing `/` — the skills should
appear in the list. If `/setup-matt-pocock-skills` is missing, the install did not take.

> **Read the skill before you teach it.** `RESOURCES.md` sets the rule: read the
> *installed* `SKILL.md`, because that is the version students will actually run, and cite
> the upstream repo as the source. Under Route A the installed copy lives under
> `~/.claude/plugins/marketplaces/mattpocock/skills/`; under Route B, wherever the
> installer put it. Read `setup-matt-pocock-skills/SKILL.md` end to end before the Week 1
> session — it is about two pages, and it is the thing you will demo live.

### 2.4 Clone the course repo

```bash
gh repo clone perro-ruidoso/gh-pr-mastery
cd gh-pr-mastery
python checkers/check_site.py
```

Expected **[run 2026-09-12]**:

```
8 pages, 67 internal links checked
all checks passed
```

`check_site.py` validates internal links, asset wiring, lesson structure, and self-check
answer keys. Run it after any edit to `docs/`. It has been fault-injection tested — a
broken link, a Mermaid diagram with no library, and a `data-answer` naming a missing
option were all caught.

`check_a1.py` needs no dependencies beyond an authenticated `gh` on `PATH`. The generators
do: `objectives/build_objectives.py` needs `openpyxl` and `roadmap/build_roadmap.py` needs
`python-docx`. You need neither to teach.

> **Never hand-edit `objectives/mastery-objectives.xlsx`, `objectives/mastery-objectives.md`,
> or `roadmap/roadmap.docx`.** Each is written from a list inside its generator script, and
> a hand edit is silently discarded on the next run. Edit the Python.

---

## Part 3 — Organization setup

### 3.1 Confirm what you have

**[run 2026-09-12]** — current state of `perro-ruidoso`:

```bash
$ gh api orgs/perro-ruidoso/memberships/acatlin --jq '{role,state}'
{"role":"admin","state":"active"}

$ gh repo list perro-ruidoso --json name,visibility,isTemplate
[{"isTemplate":false,"name":"gh-pr-mastery","visibility":"PUBLIC"},
 {"isTemplate":true,"name":"flashcards-seed","visibility":"PUBLIC"}]

$ gh api repos/perro-ruidoso/gh-pr-mastery/pages --jq '{status,html_url,source}'
{"html_url":"https://perro-ruidoso.github.io/gh-pr-mastery/",
 "source":{"branch":"main","path":"/docs"},"status":"built"}
```

Both repos public, the Seed Repo flagged as a template, the site built and serving from
`main /docs`. That is the state the course needs, and it is already true.

### 3.2 Two things that are *not* yet done

**[run 2026-09-12]**, both of these returned empty:

```bash
$ gh api orgs/perro-ruidoso/public_members --jq '.[].login'      # (nothing)
$ gh api orgs/perro-ruidoso/teams --jq '.[].slug'                # (nothing)
```

**Your own membership is private.** You require this of every student in A1 item 2, the
checker enforces it, and M01 justifies it. Fix yours first — a cohort notices. Web UI:
organization → **People** → find yourself → the Private/Public control in your row →
**Public**. CLI **[untested]**:

```bash
gh api -X PUT orgs/perro-ruidoso/public_members/acatlin
```

Confirm with the same call the checker makes:

```bash
gh api orgs/perro-ruidoso/public_members/acatlin --silent && echo public
```

**There are no teams.** You do not need one for Week 1. You *will* need one in Week 5, to
grant the cohort write access on `flashcards-upstream` (`adr/0004`). Creating it now is
cheap and means the invitation flow runs once rather than twice. Web UI: organization →
**Teams** → **New team** → name it `cohort-2026`, visibility **Visible**.

### 3.3 Invite students

You need each student's **GitHub handle** (or email). Collect handles at enrolment — the
checker is keyed on the handle, so collecting them early saves a round trip later.

Web UI, recommended the first time: organization → **People** → **Invite member** → enter
handle or email → role **Member** → optionally add to `cohort-2026`. CLI **[untested]**:

```bash
gh api -X POST orgs/perro-ruidoso/invitations \
  -f email='student@example.edu' -f role=direct_member
```

Track who has not accepted:

```bash
gh api orgs/perro-ruidoso/invitations --jq '.[] | {login,email,created_at}'
```

**[run 2026-09-12]** this returned `0` pending invitations.

Then, as students accept:

```bash
gh api orgs/perro-ruidoso/members        --jq '.[].login'   # accepted
gh api orgs/perro-ruidoso/public_members --jq '.[].login'   # accepted AND public
```

**The gap between those two lists is your Week 1 nag list.** A student in the first but not
the second has done half of A1 item 2 and will lose an hour in Week 5.

### 3.4 Repository settings to leave alone

`seed/SPEC.md` §8 is explicit, and every item is deliberate:

- **No rulesets, no branch protection, no CODEOWNERS** on the Seed Repo. Students
  configure those themselves on their own Instance in Week 5 (M26, M27). Adding them
  removes the objective.
- **No Actions secrets.** The Claude GitHub Action is instructor-funded on
  `flashcards-upstream` only (`adr/0004`), which does not exist yet.
- **No `docs/agents/`, no `## Agent skills` section in `CLAUDE.md`, no triage labels** in
  the template. Those are A1 items 3 and 4. Audit before touching the template — both of
  these must print nothing:

```bash
git ls-files | grep docs/agents
grep -rn 'needs-triage' .
```

---

## Part 4 — Verify the infrastructure end to end

Forty-five minutes that will save you a bad first session. Doing exactly this, as a
throwaway student, is how the two real bugs in this course were found.

### 4.1 The site

```bash
python checkers/check_site.py
```

Then open <https://perro-ruidoso.github.io/gh-pr-mastery/> and click through Course Home →
Week 1 hub → M01. Confirm the Mermaid diagrams render (M02 and M03 both have one) and that
a self-check reveal button works. `check_site.py` validates the wiring but not the
rendering.

### 4.2 The Seed Repo

```bash
gh repo view perro-ruidoso/flashcards-seed --json isTemplate,visibility,defaultBranchRef
gh issue list --repo perro-ruidoso/flashcards-seed --state open --json number --jq 'length'
```

**[run 2026-09-12]** the issue count is `15`. All fifteen backlog tickets are filed, with
**19 blocking edges** recorded as real GitHub issue dependencies. The graph was re-derived
from what GitHub stores — not from the script that wrote it — and reproduces
`seed/SPEC.md` §6's answer key: **5 waves, maximum parallel width 4, five two-parent
joins** at T04, T06, T08, T10, T13. Week 1 does not use the backlog; Week 2 does.

### 4.3 Walk A1 yourself, as a student

Create a throwaway Instance and do every A1 step exactly as written. Use a handle-shaped
name so the checker can find it:

```bash
gh repo create perro-ruidoso/flashcards-instrtest \
  --template perro-ruidoso/flashcards-seed \
  --public --clone
cd flashcards-instrtest
git log --oneline          # exactly one commit — template behaviour, confirmed not assumed
python -m venv .venv
source .venv/bin/activate  # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -e ".[dev]"
pytest -q
```

The Seed Repo's suite is **20 tests in 0.18 s** locally, with `ruff` and `mypy --strict`
clean and zero runtime dependencies. CI on the initial push was green in **24 s** on
CPython 3.12.14.

Then run the checker against your throwaway. **This is the important part** — it must fail
on exactly the student-produced items and pass on repo shape:

```bash
python checkers/check_a1.py --org perro-ruidoso --handle instrtest
```

Expect *Instance exists*, *Public*, and *Created from template* to pass, and failures on
the three `docs/agents/` files, the triage labels, and the write-up. **If it passes the
`docs/agents` checks, the template is wrong** and you have lost an objective.

Now finish the assignment as a student would — run `/setup-matt-pocock-skills` inside
`claude`, commit, create the labels, write a short `a1-writeup.md` — and re-run the checker
until everything is green. You now know exactly what your students are about to
experience, including how long it takes.

> **Wait a few seconds before checking labels.** Labels take a moment to appear on a newly
> created repository. An immediate `gh label list` returned an empty set during the build;
> the same call moments later returned all ten. A grader running `check_a1.py` seconds
> after a student creates their Instance can see a spurious label failure.

### 4.4 Clean up

Throwaway repos are clutter, and on a public org, visible clutter.

```bash
gh auth refresh -s delete_repo
gh repo delete perro-ruidoso/flashcards-instrtest --yes
```

Two such repos from the original template smoke test (`flashcards-smoketest`,
`flashcards-labelprobe`) have already been deleted; the org now holds `flashcards-seed` and
`gh-pr-mastery` only, which the `gh repo list` in 3.1 confirms.

---

## Part 5 — Linear, from zero

**You do not need Linear in Week 1.** It is wired in at the *end of Week 2* (M12),
deliberately, so students accumulate real GitHub history before the PM layer arrives and
so Week 6 has something to examine. Read this section during Week 1 anyway, because it
contains the one unresolved decision that can derail Week 2.

### 5.1 What Linear is, and what it is *not* here

Linear is a commercial issue tracker with its own model: **teams** own **issues**, issues
roll up into **projects**, and work is time-boxed into **cycles**. It is not GitHub with a
nicer skin — the two models genuinely disagree, which is the entire content of M33.

In this course Linear is the **project-management layer above GitHub**, never the source of
truth. `MISSION.md` is unambiguous: **GitHub Issues is the source of truth**; Linear sits
on top. That is why M05 tells students to answer "GitHub" when `/setup-matt-pocock-skills`
asks where issues live — the engineering skills support GitHub, GitLab, and local markdown
natively, and Linear would fall under "other," where you describe the whole workflow in
prose and maintain it by hand. Week 6's M35 asks students to defend that choice, or argue
against it.

### 5.2 Your setup

1. Create a workspace at <https://linear.app> on the **Free** plan.
2. Create one team (e.g. `FLASH`). Its key becomes the issue prefix, `FLASH-12`.
3. Install the GitHub integration: **Settings → Features → Integrations → GitHub**,
   authorize, and connect the repository.

Steps 1–3 are **[untested]** here — they are UI flows, and `CONTEXT.md`'s rule for vendor
UI is that screenshots rot, so Week 2's Learning Pages will carry dated captures under
`docs/assets/shots/` rather than prose. Walk the flow yourself and note what the current UI
actually says.

### 5.3 The two capabilities, and the open question

Confirmed from Linear's own documentation **[verified 2026-09-12 against `linear.app/docs/github`]**:

1. **PR/commit linking.** Branch names, PR titles, and magic words (`Fixes`, `Closes`,
   `Refs`, `Relates to`) drive issue status through draft → open → review → merged. This is
   what M34 assesses, and it is the load-bearing half.
2. **GitHub Issues Sync.** Bidirectional sync of title, description, status, assignees,
   labels, and comments between a Linear team and a GitHub repo. It "only syncs issues
   going forward" — pre-existing issues do not backfill.

**Open:** Linear's documentation does not state which **plan** includes Issues Sync. M12
currently assumes a student on Free can complete the wiring. **Confirm this against
`linear.app/pricing` with a real Free workspace before Week 2's M12 is written.** If Sync
turns out to be paid-only, M12 falls back to PR/commit linking alone — which is sufficient
for the status-automation objective M34 — and Week 6's sync content becomes something you
demo rather than something students do. Record the answer in `NOTES.md` with its date, and
delete the open question.

### 5.4 What to tell students in Week 1

One sentence: *"Create a free Linear account this week; we wire it to your repository at
the end of Week 2."* That is all. Do not demo it. Introducing a second tracker before
students are fluent in the first is the fastest way to manufacture the
duplication-and-sync-lag confusion that M35 exists to teach them to reason about.

---

## Part 6 — Onboarding students

### 6.1 Before enrolment

`adr/0003` requires it and the roadmap lists it as a pre-cohort task: **the syllabus must
state that all student work is world-readable, before enrolment, not after.** Every course
repository is public. That is a requirement, not a preference — merge queue (Week 5, M29)
is available in any public repository owned by an organization but requires GitHub
Enterprise Cloud for a private one. The corollary students must hear in plain language:
**nothing personal goes in these repos.** The flashcards domain was chosen partly for that.

State the three things students provide: a **Claude Pro subscription** (~$20/month), a
**Linear account** (free), and a **GitHub account** to be added to the course org.

### 6.2 Send `instructors/student-setup.md`

`instructors/student-setup.md` in this repo is written to be sent to students verbatim,
about a week before Week 1. It covers installs, `gh` authentication and scopes, the skills
plugin, accepting the org invitation, and making membership public — everything that is
slow, boring, or likely to fail on one specific machine, moved off the live session.

Tell them to finish it **before** the first meeting and to bring the output of
`gh auth status`. Assume 30–50% will not. Part 7.1 budgets for that.

### 6.3 The failures you will actually see

| Symptom | Cause | Fix |
|---|---|---|
| `gh: command not found` | Not installed, or installed without a shell restart | Restart the terminal first; reinstall second |
| `gh auth status` shows no `read:org` | Logged in before the scope was needed | `gh auth refresh -s read:org` |
| `Could not resolve to a Repository` | Instance not created, or named wrong | Name must be exactly `flashcards-<handle>` |
| Instance is private | `--public` omitted | `gh repo edit <repo> --visibility public --accept-visibility-change-consequences` |
| Instance is a fork | Clicked **Fork** instead of using the template | Delete and recreate with `--template` |
| `/setup-matt-pocock-skills` not found | Skills not installed, or installed for a different agent | `/plugin install mattpocock-skills`, restart `claude` |
| Every skill appears twice | Both install routes used | Remove one; keep the plugin |
| `gh label create` errors on `wontfix` | It is a GitHub default and already exists | Harmless — see decision 0.3(b) |
| Checker reports labels missing seconds after creation | Propagation delay | Wait, re-run |
| Multi-line commands fail on Windows | `\` line continuation is bash; PowerShell uses a backtick | Put it on one line, or use Git Bash |
| A1's `for L in ...` label loop fails | It is bash | Use the PowerShell form in the student handout |
| Org membership check fails though they accepted | Membership still private | People → their row → **Public** |

---

## Part 7 — Teaching Week 1

**Objectives:** M01 Setup (Apply) · M02 The PR model (Understand) · M03 Diffs (Understand)
· M04 Tooling (Apply) · M05 Agent config (Apply) · M06 Evidence (Analyze).
**Assessed by:** A1, due before the Week 2 meeting.

The week's thesis, from the Week 1 hub: most people who have used GitHub for a year hold a
fuzzy model of the pull request — *"a request to merge my branch."* Close enough to open a
PR, wrong enough to produce the three confusions this course keeps hitting: *why does my PR
show a file I never touched?*, *why did my PR change when someone else merged?*, and *what
exactly am I comparing against?* Week 1 replaces the fuzzy model with a precise one.

**Teach M02 and M03 as the core.** They are the week's only two "Understand" objectives and
everything later leans on them. M01, M04, and M05 are setup and tooling — important, but
students can do them from the pages alone. Spend your live time on the conceptual half and
on unblocking machines.

### 7.1 A 90-minute first session

| Time | Segment | Notes |
|---|---|---|
| 0:00–0:10 | Welcome; the course's premise; **your work is public** | Say the public-repos requirement out loud, with the merge-queue reason. Do not let it arrive as a surprise in a checker. |
| 0:10–0:25 | **Setup clinic** | Everyone runs `gh auth status` and shows the scopes line. Pair the stuck with the finished. Budget the full 15 minutes; you will need them. |
| 0:25–0:35 | M01 — three repos; template vs fork | Draw the three boxes. Everyone runs the `gh repo create --template` line, then `git log --oneline` to see the single commit. |
| 0:35–1:00 | **M02 + M03 — the conceptual core** | Chalk talk plus the live demo in 7.2. Go slowly. The highest-value 25 minutes of the week. |
| 1:00–1:12 | M04 — reading work from the terminal | Live demo in 7.3, against `cli/cli`. |
| 1:12–1:22 | M05 — configure the skills | Live-run `/setup-matt-pocock-skills` on your throwaway Instance. |
| 1:22–1:30 | M06 + A1 walkthrough | Show the exhibit (7.4), read A1's rubric aloud, take questions. |

If you have only 60 minutes: cut the M04 demo — the page is self-contained and every
command in it is reproducible — and shorten the setup clinic to a triage ("who is
blocked?") with a follow-up office hour.

### 7.2 Live demo: the merge base (M03)

The demo worth rehearsing. It builds a two-branch repo from nothing in three commits and
makes two-dot versus three-dot visible. **[run 2026-09-12 — the output below is this
script's actual output]**

```bash
mkdir mbdemo && cd mbdemo
git init -q -b main
printf 'shared line\n' > shared.txt
printf 'original\n'    > untouched.txt
git add -A && git commit -qm "Initial commit"

git switch -qc feature
printf 'my new line\n' >> shared.txt
git commit -qam "Add my line to shared.txt"

git switch -q main
printf 'CHANGED BY SOMEONE ELSE\n' > untouched.txt
git commit -qam "Someone else edits untouched.txt"
```

Now the four commands that carry the lesson:

```bash
$ git log --all --oneline --graph
* 235be8b Add my line to shared.txt
| * caec825 Someone else edits untouched.txt
|/
* 19e559c Initial commit

$ git merge-base main feature
19e559c634a92dc066ae7ae81479074f92dc0c5e

$ git diff main..feature --stat
 shared.txt    | 1 +
 untouched.txt | 2 +-
 2 files changed, 2 insertions(+), 1 deletion(-)

$ git diff main...feature --stat
 shared.txt | 1 +
 1 file changed, 1 insertion(+)
```

**The beat to land:** two dots claims you touched `untouched.txt` — and if you show
`git diff main..feature` in full, it reads as though you *deleted a colleague's work and
restored the old text*. You did not. Three dots shows one file, one line: what your branch
actually introduced. **A pull request always uses three dots.** That is why your diff stays
stable while `main` moves, and why the Files-changed tab is computed from the merge base.

Your hashes will differ from the ones above; the shapes will not.

### 7.3 Live demo: reading work from the terminal (M04)

All against `cli/cli`, so it works before anyone's Instance has history. Three moves:

```bash
gh pr list -R cli/cli --limit 3
gh pr view 14398 -R cli/cli --json number,title,state,isDraft,baseRefName,headRefName,changedFiles
gh pr view 14398 -R cli/cli --json nope        # errors, and lists every real field
```

Three things to point at:

- In the list output, a head written `owner:branch` means a **cross-repository** PR — the
  head branch lives in a contributor's fork.
- `"baseRefName": "trunk"`. The `cli/cli` default branch is not `main`. **Read the base;
  never assume it.** Every habit built on the word "main" breaks eventually — and breaks on
  purpose in Week 3, where a stacked PR's base is another feature branch.
- Asking for a bogus field is the fastest way to discover what a `gh` command can return.
  It works for `gh issue view`, `gh pr list`, and `gh run list` too.

One live-demo risk: `cli/cli` is a real, moving repository. PR 14398 was open on 2026-09-12
and may have merged since. Re-run every command in this section the morning of the session,
and if a number has gone stale, pick a current one with `gh pr list`. The Learning Pages
carry the captured transcripts, so a stale live demo is an annoyance, not a gap.

### 7.4 Live demo: the exhibit (M06)

M06 is the week's only **Analyze** objective and the one students find hardest, because it
asks them to infer *process* from *artifacts* rather than to run a command.

The worked example on the page is `cli/cli#14404` / `#14429`, and the whole page rests on
one observation: the PR merged at `15:55:40` and the issue closed at `15:55:42`. **Two
seconds.** Nobody closed that issue by hand — a linking keyword in the PR body closed it.

Then show the same thing in this course's own repository, which is the exhibit A1 item 6
actually points at **[run 2026-09-12]**:

```bash
gh pr list --repo perro-ruidoso/gh-pr-mastery --state merged \
  --json number,title,mergedAt,headRefName
```

Four merged PRs: #3, #5, #6, #8. PR #3 merged at `15:27:45`; issue #1 closed at `15:27:46`
— a **one-second gap**, the same evidence, produced here by a `Closes` keyword. Then show
the dependency:

```bash
gh api repos/perro-ruidoso/gh-pr-mastery/issues/2/dependencies/blocked_by \
  --jq '.[] | "#\(.number) [\(.state)] \(.title)"'
```

Issue #2 is recorded as blocked by #1 — a real Issue Dependency, the same mechanism the
Seed Repo's backlog uses, which is what makes A1 item 6's second question answerable from
data rather than from prose.

**Be honest about the exhibit's limits, out loud.** The M06 page was rewritten specifically
because it over-claimed: an earlier draft said each of the course's six units was filed as
a spec issue, decomposed with blocking edges, built on a branch, reviewed, and merged. That
was false and trivially falsifiable by any student running `gh pr list` — on a page whose
entire subject is *not asserting what the artifacts fail to show*. The history is short,
the first commit is a squashed import that demonstrates nothing about process, and the
pages now say so. **Model the correction in class.** A well-argued criticism of the course
repository's own process earns full marks on A1; the repository is an exhibit, not a model
answer.

As the history grows, re-audit M06's claims about what the repository demonstrates. That
claim has to stay true.

### 7.5 Per-objective teaching notes

**M01 — Instance and toolchain.** The template-versus-fork contrast is the teachable idea,
not the mechanics. A template copy "starts with a single commit" and has no ongoing link; a
fork carries the full history, stays linked, and its commits do **not** appear in the
contributions graph. Template is right here because from Week 3 onward students' history is
the thing being read and graded. Have everyone run `git log --oneline` and see the one
commit — confirmed from their own terminal rather than taken on faith. Expect one student
to fork instead; catching it in the first session costs two minutes, catching it in Week 3
costs an hour.

**M02 — What a PR actually is.** The definition to drill: *a pull request is a proposal to
merge one specific ref into one specific other ref, and it names both* — base (where it
would go) and head (what you are offering). The correction most students need is that a PR
is **not a bundle of changes**; it is a live comparison between two moving refs. Push to the
head and the PR updates itself. That is why a PR can change while you sleep, and it is the
setup for M03.

**M03 — The merge base.** See 7.2. If students take one thing from Week 1, make it this.

**M04 — Reading work from the terminal.** Frame it as three benefits, not as CLI advocacy:
**precision** (one command instead of twenty clicks), **structure** (`--json` gives data you
can filter, count, and assert on — every checker in this course is built from it), and
**agent parity** (when Claude works with GitHub it runs these same commands, so reading
them fluently is how you supervise your agent).

**M05 — Configuring the skills.** Three decisions, and the reasoning matters more than the
answers. **A: GitHub** as the issue tracker, with **no** to "PRs as a request surface"
(nobody else contributes to their Instance; they flip it to yes in Week 6 on the shared
repo). **B: accept the five canonical triage labels** — the mapping exists so that a repo
already using, say, `bug:triage` can point the skills at its own vocabulary instead of
growing duplicates, but a fresh Instance should use the canonical strings. **C:
single-context** domain docs — the Instance is one small app with a `CONTEXT.md` already
shipping in the template; multi-context is for monorepos with genuinely separate frontend
and backend vocabularies.

Two things to emphasize. First, the skill shows a draft before writing, and students should
read it — "do not accept defaults you have not understood" is the instruction on the page
and the meta-lesson of the course. Second, **`ready-for-agent` is the label that carries
the weight**: it asserts that a fresh session with no memory of the originating
conversation can execute the issue with no further human context. Week 2 is largely about
earning the right to apply it, and the gap between an issue you understand and an issue
that label describes is where most agentic work quietly fails.

Also worth a sentence, because it trips up more automation than any other GitHub quirk:
**issues and pull requests share one number space**, so a bare `#42` may be either. Scripts
should try `gh pr view 42` and fall back to `gh issue view 42`.

**M06 — Reading the exhibit.** See 7.4.

### 7.6 Questions you will be asked

**"Why does my repo have to be public? I don't want my homework on the internet."**
Because merge queue — which Week 5 (M29) requires — is available in any public repository
owned by an organization but needs GitHub Enterprise Cloud for a private one. It is a
curriculum requirement, documented in `adr/0003`, and it was in the syllabus before
enrolment. Public repos also run Actions for free, which matters in Week 5 when students
re-run CI repeatedly getting a ruleset right. Nothing personal goes in these repos.

**"Can I just use the website instead of the CLI?"** For reading, yes — the web UI is
excellent. But `--json` output is what every assignment checker in this course is built
from, and it is what your agent uses. If you find yourself clicking through the UI for A1
item 4, re-read M04.

**"Can Claude do my assignment?"** Yes, for any part, including the write-up — and you
should use it. But the analysis has to be yours in the sense that you can defend it at the
Week 2 meeting. Agentic text that over-reads the evidence is exactly what the rubric
penalises. (That wording is already in A1; quote it.)

**"What's the difference between a token scope and a repository permission?"** A scope is
what your *token* is permitted to ask for; a permission is what your *account* is allowed
to do. Only the first is yours to change, with `gh auth refresh -s`. This is A1's
self-check question 4, and getting it backwards is the most common conceptual error in
Week 1 tooling.

**"Why GitHub Issues and not Linear, if we're learning Linear?"** Because the engineering
skills support GitHub natively and Linear only as freeform prose you maintain yourself, and
because the course's premise is one source of truth with a PM layer above it. Week 6's M35
asks you to defend that — or argue against it.

---

## Part 8 — Assignment A1

**Covers** M01, M04, M05, M06. **Due** before the Week 2 meeting. Items 1–5 are graded by
script; item 6 by you, against the rubric in `assignments/a1.md`.

Students can and should run the checker themselves — A1 says so. Tell them again in class.
It converts "did I do this right?" from an email to you into a command.

### 8.1 Running the checker

One student:

```bash
python checkers/check_a1.py --org perro-ruidoso --handle alice
```

The whole cohort — one handle per line in a text file:

```bash
python checkers/check_a1.py --org perro-ruidoso --handles handles.txt
```

Machine-readable, for a gradebook:

```bash
python checkers/check_a1.py --org perro-ruidoso --handles handles.txt --json
```

It exits **non-zero if any student has a failing check** **[run 2026-09-12]**, so it can be
wired into CI later. It requires an authenticated `gh` on `PATH` and nothing else.

Real output for a student who has done nothing **[run 2026-09-12]**:

```
acatlin  [FAIL]
  fail Instance exists  perro-ruidoso/flashcards-acatlin: GraphQL: Could not resolve to a
       Repository with the name 'perro-ruidoso/flashcards-acatlin'. (repository)
  fail Org membership public  not a public member (private membership breaks Week 5 - see M01)

0/1 passing
needs work: acatlin
```

Note that the checker short-circuits: if the Instance does not exist, the file, label, and
write-up checks are skipped and only the org-membership check still runs. A two-line
failure means "nothing to grade yet," not "two problems."

### 8.2 What each check actually asserts

| Check | A1 item | Asserts |
|---|---|---|
| Instance exists | 1 | `<org>/flashcards-<handle>` resolves |
| Public | 1 | `visibility == "PUBLIC"` |
| Created from template | 1 | not a fork, and `templateRepository` composes to `<org>/flashcards-seed` |
| File `docs/agents/issue-tracker.md` | 3 | present on the default branch |
| File `docs/agents/triage-labels.md` | 3 | present on the default branch |
| File `docs/agents/domain.md` | 3 | present on the default branch |
| `CLAUDE.md` has `## Agent skills` | 3 | that literal heading appears |
| Triage labels (5) | 4 | all five label strings exist |
| `a1-writeup.md` present | 6 | present at the repo root |
| Write-up length | 6 | ≥ 250 words |
| Terminal evidence pasted | 5 | the text contains both `"baseRefName"` and `"headRefName"` |
| Cites artifacts (indicative) | 6 | contains `#`, `gh pr`, or `gh issue` — **advisory only**, for you |
| Org membership public | 2 | the handle appears in the org's public members |

Two notes on that table. **"Cites artifacts" is indicative, not pass/fail** — it renders as
a neutral marker and exists to flag a write-up that reads as ungrounded narration before you
open it. And **"Created from template"** is the check that had a real bug: it read
`templateRepository.nameWithOwner`, a field `gh repo view --json templateRepository` does
not return (it returns `{id, name, owner{id, login}}`), so the value was always `None` and
**every student would have failed on a correctly-created Instance**. It was fixed by
composing `owner.login` + `name`. If you ever see that check fail across the whole cohort at
once, suspect the checker before the students.

### 8.3 Grading item 6

Item 6 is ~300 words on **one merged pull request** in `perro-ruidoso/gh-pr-mastery`,
answering three questions: what did it change, what was it blocked by and how is that
dependency recorded, and how can you tell. Every claim names the artifact supporting it.
The four-row rubric in `assignments/a1.md` is the instrument — Grounding, Inference,
Dependency reading, Judgment. Some calibration:

**Excellent** quotes fields and timestamps: *"PR #3 merged at `15:27:45` and issue #1 closed
at `15:27:46`; a one-second gap means the `Closes` keyword closed it, not a human."* It also
separates proof from suggestion: *"`isCrossRepository: false` proves the head branch was in
the repo; it suggests, but does not prove, that the author was a maintainer."*

**Adequate** gets the story right but asserts process the repository does not show — "this
was reviewed before merging," with no review artifact cited. Mark it down under Grounding,
and name the specific unsupported sentence.

**Not yet** narrates what probably happened. The repository is barely cited, and the
dependency question is unaddressed or answered from prose rather than from the
`dependencies/blocked_by` endpoint.

Three things worth rewarding explicitly:

- **Naming the mechanism beats naming the blocker.** A1 says so. A student who writes "I
  checked `gh api .../dependencies/blocked_by` and got `#1`, which is an Issue Dependency,
  not a sub-issue — and a sub-issue could not express this at all if the ticket had two
  blockers" has understood the week.
- **"Nothing blocked this one, and here is the evidence for that"** is a fine answer if they
  picked such a PR. Most of the four merged PRs have no recorded blocker.
- **Criticism earns full marks.** "The first commit is a squashed import of 31 files; it
  demonstrates nothing about process, and the repo's own M06 page admits this" is an
  excellent answer. Do not mark a student down for auditing you honestly — that is the
  objective.

The failure mode to penalise, and to name when you do: **over-reading a field.** Treating
`mergedAt` as evidence of review, or a green check as evidence of correctness. This is where
agentic write-ups fail most often, which A1 warns about, and which makes it worth a sentence
in your feedback rather than a silent deduction.

### 8.4 Returning grades

Give every student the checker's own line items — they are specific and actionable — plus
two or three sentences on item 6. Re-running the checker after a fix is free, so a "not yet"
on items 1–5 should be a correction rather than a penalty; the point of those items is that
the next five weeks can happen in that repository.

---

## Part 9 — Known issues and things that will bite

Consolidated. Each is written up in `NOTES.md` with its source and date.

**Verified platform behaviour you must plan around**

1. **`wontfix` is free.** GitHub's default label set — `accessibility`, `bug`,
   `documentation`, `duplicate`, `enhancement`, `good first issue`, `help wanted`,
   `invalid`, `question`, `wontfix` — arrives on every new repository. A1 item 4 therefore
   assesses four labels, not five. Decision 0.3(b).
2. **Label propagation lag.** Labels take a few seconds to appear on a newly created
   repository. Do not grade immediately after a student creates their Instance.
3. **`templateRepository` has no `nameWithOwner`.** Already fixed in `check_a1.py`; recorded
   here so that if you extend the checker you do not reintroduce it.
4. **Private org membership breaks Week 5.** Anthropic's documentation is explicit that when
   org membership is private, GitHub does not identify the person as a member, so Claude
   will not act on their request even though a team grants write access. Two minutes in
   Week 1; an hour in Week 5.
5. **Secrets are withheld from fork PRs.** "With the exception of `GITHUB_TOKEN`, secrets
   are not passed to the runner when a workflow is triggered from a forked repository."
   This broke the original Week 5/6 design and forced `adr/0004`. It is now taught
   deliberately as M30. Do not promise students agentic review on fork PRs.
6. **No `gh issue edit` flag for issue dependencies** as of `gh` 2.92.0. `gh api` only, and
   the payload takes the blocker's **database id** (`gh api repos/O/R/issues/N --jq .id`),
   not the issue number. Week 2 content; Week 1 students only read dependencies.

**Unresolved**

7. Linear Free plan and Issues Sync — Part 5.3. Blocks M12's final wording.
8. Org plan, Team versus Free — decision 0.3(a). Blocks inviting students.
9. Whether a Pro subscription absorbs the cohort's CI review volume, or Max is needed —
   Week 5 dry run.

**Not built yet**

10. Weeks 2–6 and assignments A2–A6; the two graded concept quizzes; the capstone.
11. `flashcards-upstream`, needed by Week 5.
12. The Week 4 planted-bug diff. Blocked for a structural reason worth knowing: the three
    SM-2 bugs live in `scheduler.py`, which is ticket T03's output, so the diff can only be
    authored on an Instance where T03 has landed — never against the template.
13. The merge-strategy simulator widget (Week 5), and the UI captures for rulesets, merge
    queue, and Linear settings.

**Unverified in this guide** — check on first use and correct this file: making org
membership public via `gh api -X PUT` (3.2), inviting members via `gh api -X POST` (3.3),
and every Linear UI step (5.2).

---

## Part 10 — Before you teach Week 2

1. **Resolve decision 0.3(c)** — Linear Free and Issues Sync. It is the only open question
   that blocks Week 2 content, and it takes a Free workspace and ten minutes.
2. **Re-verify the vendor-behaviour rows in `NOTES.md`.** Those are the ones that move.
   Before each cohort, not once.
3. **Re-audit M06's claims** against the course repo's history as it grows. The page
   describes the history that actually exists; keep that true.
4. **Collect A1 write-ups into a calibration set.** Two or three good ones and one
   over-reading one make the Week 4 review objectives much easier to teach, because you can
   show the cohort its own work.
5. Week 2 is M07–M12 and does not exist yet. `roadmap/roadmap.docx` has the build order;
   `objectives/mastery-objectives.md` has the objectives it must hit.

---

## Appendix A — Command crib sheet

```bash
# --- state of the world -------------------------------------------------------
gh auth status                                          # account + token scopes
gh api orgs/perro-ruidoso --jq '.plan'                  # plan and seats
gh repo list perro-ruidoso --json name,visibility,isTemplate
gh api repos/perro-ruidoso/gh-pr-mastery/pages --jq '{status,html_url,source}'

# --- roster -------------------------------------------------------------------
gh api orgs/perro-ruidoso/invitations    --jq '.[] | {login,email,created_at}'
gh api orgs/perro-ruidoso/members        --jq '.[].login'    # accepted
gh api orgs/perro-ruidoso/public_members --jq '.[].login'    # accepted AND public

# --- validate -----------------------------------------------------------------
python checkers/check_site.py
python checkers/check_a1.py --org perro-ruidoso --handle <handle>
python checkers/check_a1.py --org perro-ruidoso --handles handles.txt --json

# --- regenerate (edit the Python, never the output) ---------------------------
python objectives/build_objectives.py     # needs openpyxl
python roadmap/build_roadmap.py           # needs python-docx

# --- template hygiene (run inside flashcards-seed; both must print nothing) ---
git ls-files | grep docs/agents
grep -rn 'needs-triage' .

# --- the Week 1 demos ---------------------------------------------------------
gh pr list -R cli/cli --limit 3
gh pr view 14398 -R cli/cli --json number,title,baseRefName,headRefName,changedFiles
gh pr list --repo perro-ruidoso/gh-pr-mastery --state merged \
  --json number,title,mergedAt,headRefName
gh api repos/perro-ruidoso/gh-pr-mastery/issues/2/dependencies/blocked_by \
  --jq '.[] | "#\(.number) [\(.state)] \(.title)"'
```

## Appendix B — Where everything lives

| You want | Look in |
|---|---|
| Why the course exists, what a graduate can do | `MISSION.md` |
| The precise meaning of a course term | `CONTEXT.md` |
| A verified fact, its source, and its fetch date | `NOTES.md` |
| Which source grounds which objective | `RESOURCES.md` |
| The M01–M36 objective table | `objectives/mastery-objectives.md` |
| Why a design decision was made | `adr/` |
| Student-facing lessons | `docs/` (live at perro-ruidoso.github.io/gh-pr-mastery) |
| The A1 brief and rubric students read | `assignments/a1.md` |
| What is built, what is not, what you must decide | `roadmap/roadmap.docx` |
| How the Seed Repo is specified | `seed/SPEC.md` |
| What to send students before Week 1 | `instructors/student-setup.md` |

---

*Written against the repository state of 2026-09-12. Commands marked **[run 2026-09-12]**
were executed; those marked **[untested]** were not. Re-verify vendor behaviour before each
cohort — `NOTES.md` is the record.*
