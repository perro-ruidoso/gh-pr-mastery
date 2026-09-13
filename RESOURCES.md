# Resources

The course's trust hierarchy, as defined in `CONTEXT.md`. Every factual claim in a
Learning Page must trace to a Tier 1–4 source that was actually fetched; fetch dates and
quotes live in `NOTES.md`.

## Tier 1 — GitHub official

GitHub is the subject of this course, so its docs are primary here, not ancillary.

**URL rot, 2026-09-13.** GitHub reorganised `docs.github.com` into *reference* and *how-tos*
sections. Several URLs first recorded here now redirect (HTTP 200 via 301) to new canonical
addresses, and in at least one case the wording the lessons quoted changed with the move — see
`NOTES.md`. Rows below carry the canonical URL; Week 1 pages cite the canonical URL and were
re-quoted from the fetched text. Week 2's rows were re-checked on 2026-09-13 (two more
redirects, noted inline). The whole table was re-fetched again in the 2026-09-13 Week 1–2 audit:
three Week 3–5 rows (base branch, reviewing, CI) had moved and now carry their canonical URLs;
every other row answered 200 with no redirect. Re-check again before writing Weeks 3–6.

| Resource | URL | Used in |
|---|---|---|
| Pull requests (reference) — formerly "About pull requests"; also absorbs "About collaborative development models" | https://docs.github.com/en/pull-requests/reference/pull-requests | M02, M31 |
| Branches (reference) — formerly "About comparing branches in pull requests" | https://docs.github.com/en/pull-requests/reference/branches | M03 |
| About issues — the recorded URL now redirects here | https://docs.github.com/en/issues/tracking-your-work-with-issues/learning-about-issues/about-issues | M07 |
| Managing issue types in an organization (moved from `configuring-issues/`) | https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/managing-issue-types-in-an-organization | M08 |
| Filtering and searching issues and pull requests | https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/filtering-and-searching-issues-and-pull-requests | M08 |
| Configuring issue templates for your repository | https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/configuring-issue-templates-for-your-repository | M08 |
| Syntax for issue forms | https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/syntax-for-issue-forms | M08 (learn more) |
| Adding sub-issues | https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/adding-sub-issues | M11 |
| Creating issue dependencies — the user-facing page; the CLI flags are documented here | https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/creating-issue-dependencies | M11 |
| REST API endpoints for issue dependencies | https://docs.github.com/en/rest/issues/issue-dependencies | M11 |
| REST API endpoints for sub-issues (`sub_issue_id`, `replace_parent`) | https://docs.github.com/en/rest/issues/sub-issues | M11 |
| Creating diagrams (Mermaid in Markdown) | https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/creating-diagrams | M11 |
| Linking a pull request to an issue | https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/linking-a-pull-request-to-an-issue | M15 |
| Changing the base branch of a pull request — moved to `how-tos/` 2026-09-13 | https://docs.github.com/en/pull-requests/how-tos/create-pull-requests/changing-the-base-branch-of-a-pull-request | M16 |
| Reviewing proposed changes in a pull request — moved to `how-tos/review-pull-requests/` 2026-09-13 | https://docs.github.com/en/pull-requests/how-tos/review-pull-requests/reviewing-proposed-changes-in-a-pull-request | M19, M20 |
| Continuous integration (Actions "get started") — formerly "About continuous integration with GitHub Actions" | https://docs.github.com/en/actions/get-started/continuous-integration | M25 |
| About rulesets | https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets | M26 |
| About protected branches | https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches | M26 |
| About code owners | https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners | M27 |
| Managing a merge queue | https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/managing-a-merge-queue | M29 |
| Using secrets in GitHub Actions | https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-secrets | M02, M30 |
| Forks (reference) — formerly "About forks" | https://docs.github.com/en/pull-requests/reference/forks | M01, M31 |
| GitHub CLI manual | https://cli.github.com/manual/ | M04, M13 |
| GitHub CLI manual: `gh auth status`, `gh auth refresh` | https://cli.github.com/manual/gh_auth_refresh | M01 |
| GitHub CLI manual: `gh repo create` | https://cli.github.com/manual/gh_repo_create | M01 |
| GitHub CLI manual: `gh pr view`, `gh pr list`, `gh pr diff`, `gh help formatting` | https://cli.github.com/manual/gh_pr_view | M02, M04, M06 |
| GitHub CLI manual: `gh label create` | https://cli.github.com/manual/gh_label_create | M05, M08 |
| GitHub CLI manual: `gh issue create`, `gh issue edit`, `gh issue list` (2.94.0+ flags) | https://cli.github.com/manual/gh_issue_create | M07, M08, M09, M11 |
| GitHub CLI manual: `gh issue close` | https://cli.github.com/manual/gh_issue_close | M12 |
| GitHub CLI v2.94.0 release notes — issue types, sub-issues, and relationships | https://github.com/cli/cli/releases/tag/v2.94.0 | M08, M11 |
| Creating a repository from a template | https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-repository-from-a-template | M01 |
| Scopes for OAuth apps | https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/scopes-for-oauth-apps | M01 |
| Publicizing or hiding organization membership | https://docs.github.com/en/account-and-profile/how-tos/organization-membership/publicizing-or-hiding-organization-membership | M01 |
| Changing the stage of a pull request | https://docs.github.com/en/pull-requests/how-tos/create-pull-requests/changing-the-stage-of-a-pull-request | M02 |
| Comparing commits | https://docs.github.com/en/pull-requests/how-tos/commit-changes/comparing-commits | M03 |
| Managing labels | https://docs.github.com/en/issues/using-labels-and-milestones-to-track-work/managing-labels | M05, M08 |
| Using keywords in issues and pull requests | https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/using-keywords-in-issues-and-pull-requests | M06 |

## Tier 2 — Anthropic official

| Resource | URL | Used in |
|---|---|---|
| Code Review (`/code-review`) | https://code.claude.com/docs/en/code-review | M21 |
| Claude Code GitHub Actions | https://code.claude.com/docs/en/github-actions | M30 |
| Memory / CLAUDE.md | https://code.claude.com/docs/en/memory | M05 |
| Skills | https://code.claude.com/docs/en/skills | M05, M09, M18 |

## Tier 3 — Pocock / AI Hero

| Resource | URL | Used in |
|---|---|---|
| `mattpocock/skills` repo — Week 2 quotes the installed `to-spec` and `to-tickets` | https://github.com/mattpocock/skills | M05, M07, M09, M10, M17, M18, M24, M32 |
| AI Hero | https://www.aihero.dev | M10, M18 |

Local copies of the skills this course teaches are at `~/.agents/skills/`, symlinked into
`~/.claude/skills/`. Read the installed `SKILL.md` when writing a lesson — it is the
version students will actually run — and cite the upstream repo as the source.

## Tier 4 — Linear official

| Resource | URL | Used in |
|---|---|---|
| GitHub integration | https://linear.app/docs/github | M12, M34 |
| Pricing (plan gates) — Issue sync is a Core feature on every plan; parsed at cell level 2026-09-13, see `NOTES.md` | https://linear.app/pricing | M12 |
| GitHub Issues Importer (historical issues; sync is forward-only) | https://linear.app/docs/github-to-linear | M12 (learn more) |

## Non-GitHub references used on Week 1 pages

| Resource | URL | Used in |
|---|---|---|
| Git reference: `git merge-base`, `git diff`, `gitrevisions` | https://git-scm.com/docs/git-diff | M03 |
| Pro Git, ch. 3.2 Basic Branching and Merging | https://git-scm.com/book/en/v2/Git-Branching-Basic-Branching-and-Merging | M03 (learn more) |
| jq manual (moved from `jqlang.github.io`; old address redirects) | https://jqlang.org/manual/ | M04, M06 (learn more) |
| Mermaid: flowchart syntax (`graph LR`, `subgraph`) | https://mermaid.js.org/syntax/flowchart.html | M11 (learn more) |

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
