# Before Week 1 — Setup

*Send this to students about a week before the first meeting. It is written to be read by
them, not about them. Instructor notes are in `instructors/instructor-guide.md`.*

---

Welcome to **GitHub Pull Requests for Agentic Coders**.

This page is the boring part: accounts, installs, and one authentication step that saves
you an hour in Week 5. **Do it before the first meeting** and bring the output of
`gh auth status` — we will spend the first fifteen minutes unblocking whoever is stuck,
and it is better not to be that person twice.

Budget **45 minutes**. Nothing here is hard; some of it is slow.

---

## Read this first: your coursework is public

Every repository in this course is a **public** repository, including yours. That is a
requirement, not a preference: merge queue, which Week 5 depends on, is available in any
public repository owned by an organization but requires GitHub Enterprise Cloud for a
private one. Public repositories also run GitHub Actions for free, which matters when you
are re-running CI to get a ruleset right.

**Put nothing personal in these repositories.** The practice application is a flashcard
CLI, chosen partly for that reason.

---

## 1. Accounts (about 15 minutes)

| Account | Cost | Notes |
|---|---|---|
| **GitHub** | free | You probably have one. Have your handle ready; the instructor needs it. |
| **Claude Pro**, with Claude Code | ~$20/month, yours | You direct an agent for all six weeks. This is the one paid requirement. |
| **Linear** | free plan | Create the account now. We do not use it until the end of Week 2 — do not go exploring yet. |

---

## 2. Install the tools (about 15 minutes)

| Tool | Minimum | Check |
|---|---|---|
| `git` | 2.30+ | `git --version` |
| Python | 3.10 or newer | `python --version` |
| GitHub CLI (`gh`) | 2.60+ | `gh --version` |
| Claude Code | current | `claude --version` |

**macOS**

```bash
brew install git gh python@3.12
npm install -g @anthropic-ai/claude-code
```

**Windows** (PowerShell)

```powershell
winget install --id Git.Git
winget install --id GitHub.cli
winget install --id Python.Python.3.12
npm install -g @anthropic-ai/claude-code
```

**Linux** — use your package manager for `git` and `python3`; install `gh` from
<https://cli.github.com>, and Claude Code with the `npm` line above.

**Restart your terminal** after installing. Roughly half of all "command not found"
problems are a shell that has not reloaded its `PATH`.

> **Windows: which shell?** Every command in this course is written for **bash**. Windows
> installs **Git Bash** alongside Git, and using it means the transcripts in the lessons
> work verbatim. PowerShell is fine too, but a few things differ — line continuations use
> a backtick instead of `\`, and loops are written differently. Where it matters, this
> page gives both.

---

## 3. Authenticate `gh` (about 5 minutes — the important one)

```bash
gh auth login
```

Choose **GitHub.com**, protocol **HTTPS**, and authenticate in the browser. Then:

```bash
gh auth status
```

You should see something like this:

```
github.com
  ✓ Logged in to github.com account your-handle (keyring)
  - Active account: true
  - Git operations protocol: https
  - Token: gho_************************************
  - Token scopes: 'gist', 'read:org', 'repo', 'workflow'
```

**Read the last line.** Those four scopes — `gist`, `read:org`, `repo`, `workflow` — are
what the course needs through Week 4. If `repo` or `read:org` is missing, nothing else
works. Add a scope without logging in again:

```bash
gh auth refresh -s read:org
```

> A **scope** is a permission attached to your *token* — what the token is allowed to ask
> for. It is not the same thing as a repository **permission**, which is what your
> *account* is allowed to do. Only the first one is yours to change. You will be asked
> about this distinction.

**Bring the scopes line to the first meeting.**

---

## 4. Install the engineering skills (about 5 minutes)

The course uses a family of Claude Code skills — `/to-spec`, `/to-tickets`,
`/code-review`, `/qa`, `/triage`, and others — that form the workflow spine of Weeks 2
through 6. Install them once, on your machine.

Start Claude Code anywhere:

```bash
claude
```

and run:

```
/plugin install mattpocock-skills
```

It is in Claude Code's official marketplace, so there is nothing to add first, and updates
arrive automatically.

**Check it worked.** Restart `claude`, type `/`, and look for
**`setup-matt-pocock-skills`** in the list. That is the one you need for Week 1, and the
assignment cannot be completed without it.

> There is a second install route (`npx skills@latest add mattpocock/skills`) that copies
> editable files into a project instead. **Do not use both** — you will end up with every
> skill twice. Use the plugin.

---

## 5. Join the course organization (2 minutes, plus waiting)

You will receive an email invitation to the **`perro-ruidoso`** organization. Accept it.

Then — and this is the step people skip — **make your membership public**:

1. Go to the organization's **People** tab.
2. Find yourself in the list.
3. Change your membership visibility from **Private** to **Public**.

**Why it matters.** GitHub hides organization membership by default. When yours is
private, other tools cannot see that the organization grants you write access — including
the Claude GitHub App we use in Week 5, which will simply refuse to act on your comments.
It is two minutes now and a confusing hour later. The Week 1 assignment checks it.

Verify from the terminal:

```bash
gh api orgs/perro-ruidoso/public_members/your-handle --silent && echo "public ✓"
```

---

## 6. Create your Instance (about 10 minutes)

Your **Instance** is your own copy of the course's template repository — a small Python
flashcard CLI with tests and CI. You work in it for six weeks.

Replace `<your-handle>` with your GitHub handle, exactly:

```bash
gh repo create perro-ruidoso/flashcards-<your-handle> \
  --template perro-ruidoso/flashcards-seed \
  --public \
  --clone
```

On PowerShell, put it on one line (or replace each `\` with a backtick):

```powershell
gh repo create perro-ruidoso/flashcards-<your-handle> --template perro-ruidoso/flashcards-seed --public --clone
```

Three things to get right, because the assignment checker enforces all three:

- The name is **exactly** `flashcards-<your-github-handle>`.
- It is **`--public`**. Not a typo, not laziness — see the note at the top.
- It is created **from the template**, with `--template`. **Do not fork.** A template copy
  starts with a single commit and is yours; a fork carries the original's whole history
  and stays tied to it. We use a fork deliberately in Week 6, and the contrast is part of
  the course.

Then confirm the template behaviour from your own terminal rather than taking it on faith:

```bash
cd flashcards-<your-handle>
git log --oneline
```

One commit. That is what a template copy looks like.

### Run the tests once

Not because you will write Python — you will mostly direct Claude to — but so that when
CI fails in Week 5 you know it is CI's fault and not your machine's.

```bash
python -m venv .venv
source .venv/bin/activate          # Windows PowerShell: .venv\Scripts\Activate.ps1
                                   # Windows Git Bash:   source .venv/Scripts/activate
pip install -e ".[dev]"
pytest -q
```

Green. It takes under a second.

### Say hello to your agent

```bash
claude
```

Then ask it to describe the project. It will read the `CLAUDE.md` and `CONTEXT.md` that
ship with the template — which is why an agent can be useful here on its first turn
instead of its tenth.

---

## 7. Check yourself

The course ships the same checker your instructor grades with, so you never have to
wonder. From a clone of the course repo:

```bash
gh repo clone perro-ruidoso/gh-pr-mastery
cd gh-pr-mastery
python checkers/check_a1.py --org perro-ruidoso --handle <your-handle>
```

It prints one line per check. After finishing this page you should see **Instance
exists**, **Public**, **Created from template**, and **Org membership public** all
passing. The rest — the `docs/agents/` files, the triage labels, the write-up — is
assignment A1, which you do during Week 1. Failures there right now are expected.

> If it reports a missing label seconds after you created something, wait a moment and
> re-run. Labels take a few seconds to appear on a new repository.

---

## Done — what you should have

- [ ] GitHub, Claude Pro, and Linear accounts
- [ ] `git`, Python 3.10+, `gh`, and Claude Code installed, each answering `--version`
- [ ] `gh auth status` showing `repo` and `read:org` in the token scopes
- [ ] `/setup-matt-pocock-skills` visible in Claude Code's slash-command list
- [ ] Organization invitation accepted, membership set to **Public**
- [ ] `flashcards-<your-handle>` created from the template, public, cloned locally
- [ ] `git log --oneline` showing exactly one commit
- [ ] `pytest -q` green in your Instance
- [ ] The scopes line from `gh auth status`, ready to show at the first meeting

Anything unticked is a question for the first fifteen minutes of the meeting. Bring the
exact error text — "it didn't work" is hard to help with, and reading an error precisely
is most of what the next six weeks are about.

---

## Reference

The course site: <https://perro-ruidoso.github.io/gh-pr-mastery/>. Week 1's first lesson,
**M01 — Your Instance and Your Toolchain**, covers everything on this page in more depth,
including why each step is what it is.
