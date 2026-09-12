# Mission: GitHub Pull Requests for Agentic Coders

A six-week, cohort-taught mastery course in which students learn to run real
development work through GitHub pull requests while directing Claude Code as the
implementer. The subject is the **workflow** — issues, dependency structure,
branches, diffs, review, gates, and the project-management layer above them —
not the application being built.

## Why

An agentic coder's bottleneck is no longer typing code. It is **specifying work
small enough to hand over, and reviewing what comes back**. Pull requests are
where both happen. A student who can decompose a spec into tickets with honest
dependency edges, hand one ticket to a fresh agent session, and then own the
resulting diff has the skill that actually scales; a student who cannot is
limited to whatever a single conversation can hold.

## Success looks like

A graduate can, unaided:

- Decompose a spec into tracer-bullet tickets with declared blocking edges, and
  read that graph to say which tickets could be handed to concurrent agent sessions.
- Take one ticket through branch → implementation by Claude → PR → review → merge,
  with the issue closing itself on merge and the tracker updating without being touched.
- Stack a dependent PR, retarget it when its parent merges, and resolve the conflict
  that follows.
- Review someone else's PR — reading `/code-review` findings critically rather than
  deferring to them — and write comments the author can act on without asking a question.
- Configure the gates: CI, required checks, review approval, CODEOWNERS, merge queue,
  and a merge method they can justify.
- Sit in the maintainer seat: triage incoming external PRs through a state machine.
- Say where the source of truth for work should live for a given team, and defend it.

## Constraints

- **Standalone.** Assumes generic GitHub familiarity (pulls, forks, some branches).
  Does not assume the "Agentic Coding with Claude" course; re-teaches the PR/issue
  core quickly, from the workflow angle rather than as ancillary material.
- **Cohort of 8–14**, weekly live meeting, ~4 hrs/week, 6 weeks, 36 mastery objectives.
- **Students provide** a Claude Pro subscription (Claude Code), a Linear seat, and
  join the course GitHub org.
- **Every course repo is public.** The org (`perro-ruidoso`) is on GitHub Team, so rulesets
  and branch protection would work privately — but **merge queue** requires a public repo
  outside Enterprise Cloud, and M29 needs one. Public repos also run Actions for free.
  See `adr/0003`.
- **GitHub Issues is the source of truth**; Linear is the project-management layer,
  wired in at the end of Week 2 so students accumulate real history before Week 6
  examines it.
- **Everything is grounded in fetched primary sources** and tested against real
  GitHub/Linear before it ships. Verified facts are logged in `NOTES.md`.
- The course repo is **dogfooded at unit granularity**: each unit is a spec issue,
  decomposed with `/to-tickets`, built on a branch, reviewed, and merged — so its own
  issue graph and PR history are Week 1 teaching exhibits.

## Out of scope

- Supply-chain dependency graphs (Dependabot, SBOM) — a different course; the word
  "dependency" here means *work* dependencies. See `CONTEXT.md`.
- GitLab, Bitbucket, GitHub Enterprise Server.
- Teaching Python. Students direct Claude; the seed app's language is a substrate,
  not a subject.
- GitHub Projects v2 as a PM layer (Linear occupies that role).
