# Agentic CI review runs on upstream branches; forks are a separate, contrasting drill

## The problem

The design agreed in the grill session had students **fork** `flashcards-upstream` and
open cross-repo PRs, with an instructor-funded Claude GitHub Action reviewing every
incoming PR. Verification on 2026-09-12 showed that cannot work. GitHub:

> "With the exception of `GITHUB_TOKEN`, secrets are not passed to the runner when a
> workflow is triggered from a forked repository."

No secret means no `CLAUDE_CODE_OAUTH_TOKEN`, which means the review job cannot
authenticate. Anthropic's own documentation states the same consequence. Separately, the
action rejects triggering actors without **write access** to the repository — which a
fork contributor does not have.

The managed alternative, Anthropic's Code Review product, was also rejected: it requires a
Claude **Team or Enterprise** subscription (students are on Pro) and costs $15–25 per
review.

## The decision

`flashcards-upstream` is used in **two explicitly different modes**, and the difference
between them is taught rather than hidden.

**Write-access mode (Weeks 5–6, the default working mode).** Students are org members with
write access. They push branches directly to the upstream repo and open same-repo PRs.
Secrets are available, so the instructor-funded Claude GitHub Action reviews every PR and
`@claude` works in comment threads. All gate objectives (M25–M30) are exercised here.

**Fork mode (Week 6, one deliberate drill).** Students fork the upstream repo and open a
cross-repo PR, experiencing the real position of an outside contributor: no write access,
no secrets, no agentic review, and a human maintainer as the only reviewer. This is the
setting in which the maintainer rotation runs `/triage` on incoming external PRs.

## Why this is better than the original plan

The constraint is the lesson. "Why can't CI see the secret on my fork PR?" is one of the
most common real confusions in open-source contribution, and its answer — that a fork PR
is arbitrary untrusted code and a secret handed to it is a secret published — is a genuine
security insight that a student who has felt the failure will keep.

M30 is therefore written as an **Analyze** objective: read a working workflow, explain its
triggers, permissions, and secret, and explain why it cannot run on a fork PR.

## Consequences

- Students need write access on `flashcards-upstream`, granted via an org team.
- Org membership must be made **public** by each student, or they must be added as direct
  repository collaborators; Anthropic's docs note that private org membership prevents
  Claude from recognising their write access.
- The instructor generates the OAuth token with `claude setup-token` and stores it as a
  repository secret. It is tied to the instructor's personal subscription — a single point
  of failure to monitor, and a usage-limit risk to measure in the Week 5 dry run.
- The fork drill produces no automated review, by design. Its rubric grades the human
  review and the triage, not agent output.
