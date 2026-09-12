# Resources

The course's trust hierarchy, as defined in `CONTEXT.md`. Every factual claim in a
Learning Page must trace to a Tier 1–4 source that was actually fetched; fetch dates and
quotes live in `NOTES.md`.

## Tier 1 — GitHub official

GitHub is the subject of this course, so its docs are primary here, not ancillary.

| Resource | URL | Used in |
|---|---|---|
| About pull requests | https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-pull-requests | M02 |
| About comparing branches in pull requests | https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-comparing-branches-in-pull-requests | M03 |
| About issues | https://docs.github.com/en/issues/tracking-your-work-with-issues/about-issues | M07 |
| Adding sub-issues | https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/adding-sub-issues | M11 |
| Linking a pull request to an issue | https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/linking-a-pull-request-to-an-issue | M15 |
| Changing the base branch of a pull request | https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/changing-the-base-branch-of-a-pull-request | M16 |
| Reviewing proposed changes in a pull request | https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/reviewing-changes-in-pull-requests/reviewing-proposed-changes-in-a-pull-request | M19, M20 |
| About continuous integration with GitHub Actions | https://docs.github.com/en/actions/automating-builds-and-tests/about-continuous-integration | M25 |
| About rulesets | https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets | M26 |
| About protected branches | https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches | M26 |
| About code owners | https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners | M27 |
| Managing a merge queue | https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/managing-a-merge-queue | M29 |
| Using secrets in GitHub Actions | https://docs.github.com/en/actions/security-for-github-actions/security-guides/using-secrets-in-github-actions | M30 |
| About forks | https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/about-forks | M31 |
| GitHub CLI manual | https://cli.github.com/manual/ | M04, M13 |

## Tier 2 — Anthropic official

| Resource | URL | Used in |
|---|---|---|
| Code Review (`/code-review`) | https://code.claude.com/docs/en/code-review | M21 |
| Claude Code GitHub Actions | https://code.claude.com/docs/en/github-actions | M30 |
| Memory / CLAUDE.md | https://code.claude.com/docs/en/memory | M05 |
| Skills | https://code.claude.com/docs/en/skills | M18 |

## Tier 3 — Pocock / AI Hero

| Resource | URL | Used in |
|---|---|---|
| `mattpocock/skills` repo | https://github.com/mattpocock/skills | M05, M09, M10, M17, M18, M24, M32 |
| AI Hero | https://www.aihero.dev | M10, M18 |

Local copies of the skills this course teaches are at `~/.agents/skills/`, symlinked into
`~/.claude/skills/`. Read the installed `SKILL.md` when writing a lesson — it is the
version students will actually run — and cite the upstream repo as the source.

## Tier 4 — Linear official

| Resource | URL | Used in |
|---|---|---|
| GitHub integration | https://linear.app/docs/github | M12, M34 |
| Pricing (plan gates) | https://linear.app/pricing | M12 — **unresolved**, see `NOTES.md` |

## Ancillary

Used only where no primary source covers the ground, and always marked as practitioner
material on the page:

- Stacked-PR practice writing (vendor blogs) — M16. Treat claims about tooling as
  marketing; the mechanics come from GitHub's base-branch docs.
- Diff-reviewability heuristics — M14. No authoritative source exists; this is a course
  exercise built on the cohort's own PRs.

## Deliberately rejected

- **Anthropic Code Review (managed product)** — requires a Claude Team/Enterprise
  subscription and costs $15–25 per review. Students are on Pro. See `NOTES.md`.
- **GitHub Projects v2** — Linear occupies the PM role; see `MISSION.md` out-of-scope.
- **Dependabot / dependency graph / SBOM** — "dependency" in this course means *work*
  dependency. See `CONTEXT.md`.
