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
every other row answered 200 with no redirect. Re-checked again 2026-09-13 before Week 3: the Week 3
rows below answered 200 with no redirect; five *new* URLs fetched for Week 3 (merge conflicts ×3,
creating a PR, PR merges) redirected once each and are recorded at their canonical addresses.
Re-checked again in the 2026-09-14 Weeks 1–3 audit: **all 105 external URLs** on the site and in
this file answered 200 with no redirect. Re-check again before writing Weeks 4–6.

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
| Creating a branch to work on an issue (the web half of `gh issue develop`) | https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/creating-a-branch-for-an-issue | M13, M14 |
| Creating a pull request — canonical is `how-tos/create-pull-requests/`; the old `collaborating-with-pull-requests/…` path redirects | https://docs.github.com/en/pull-requests/how-tos/create-pull-requests/creating-a-pull-request | M15 |
| Merging a pull request — the note promising an automatic retarget when a merged head branch is deleted | https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/merging-a-pull-request | M16 |
| Managing the automatic deletion of branches | https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/managing-the-automatic-deletion-of-branches | M16 |
| Pull request merges (reference) — formerly "About pull request merges"; the old path redirects | https://docs.github.com/en/pull-requests/reference/pull-request-merges | M16, M28 |
| Merge conflicts (reference) — formerly `addressing-merge-conflicts/about-merge-conflicts`; redirects | https://docs.github.com/en/pull-requests/reference/merge-conflicts | M17 |
| Resolving a merge conflict using the command line — moved to `how-tos/merge-and-close-pull-requests/`; redirects | https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/resolving-a-merge-conflict-using-the-command-line | M17 |
| Resolving a merge conflict on GitHub — same move; redirects | https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/resolving-a-merge-conflict-on-github | M17 |
| Issue event types (`connected`, `base_ref_changed`, `base_ref_deleted`, `automatic_base_change_succeeded`, `merged`) | https://docs.github.com/en/rest/using-the-rest-api/issue-event-types | M15, M16 |
| REST API endpoints for timeline events | https://docs.github.com/en/rest/issues/timeline | M16 |
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
| GitHub CLI manual: `gh issue develop` (`--base`, `--name`, `--checkout`, `--list`) | https://cli.github.com/manual/gh_issue_develop | M13, M16 |
| GitHub CLI manual: `gh pr create` (base resolution: `--base`, then `gh-merge-base`, then default) | https://cli.github.com/manual/gh_pr_create | M13, M15, M16 |
| GitHub CLI manual: `gh pr edit` (`--base` retargets) | https://cli.github.com/manual/gh_pr_edit | M15, M16 |
| GitHub CLI manual: `gh pr merge` (`--squash`, `--delete-branch`) | https://cli.github.com/manual/gh_pr_merge | M16 |
| GitHub CLI manual: `gh pr diff` (no `--stat`; `--name-only`) | https://cli.github.com/manual/gh_pr_diff | M14 |
| GitHub CLI manual: `gh pr close` | https://cli.github.com/manual/gh_pr_close | M14 |
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
| Skills — `disable-model-invocation`, front-matter reference | https://code.claude.com/docs/en/skills | M05, M09, M17, M18 |

## Tier 3 — Pocock / AI Hero

| Resource | URL | Used in |
|---|---|---|
| `mattpocock/skills` repo — Week 2 quotes the installed `to-spec` and `to-tickets` | https://github.com/mattpocock/skills | M05, M07, M09, M10, M17, M18, M24, M32 |
| AI Hero | https://www.aihero.dev | M10, M18 |
| AI Hero: smart zone (the ~120k-token limit `ask-matt` links) | https://www.aihero.dev/ai-coding-dictionary/smart-zone | M18 |

Local copies of the skills this course teaches are at `~/.agents/skills/`, symlinked into
`~/.claude/skills/` — a `npx skills` snapshot dated 2026-07-09 (38 skills). Read the installed
`SKILL.md` when writing a lesson and cite the upstream repo as the source — **but note (found
2026-09-14) that students install the Claude Code plugin, whose manifest
(`.claude-plugin/plugin.json`, v1.2.3) carries 25 skills tracking upstream head, so "the version
students will actually run" is the plugin's, not this machine's.** The plugin lacks
`request-refactor-plan` and `qa` (deleted upstream 2026-08-05, commit `c66bdee`; the changeset
names `/to-spec` + `/improve-codebase-architecture` and `/triage` + `/to-tickets` as their
replacements), `git-guardrails-claude-code` (`misc`), and `claude-handoff` (`in-progress`).
See `NOTES.md`, Weeks 1–3 audit §1, for the file-by-file diff.

The installed files Week 3 quotes, all dated 2026-07-09 and read 2026-09-13; upstream
paths as of 2026-09-14, head `3cca18b` (`skills/<bucket>/<name>/SKILL.md`), with the
substantive upstream changes since the snapshot:

| Installed `SKILL.md` | Upstream bucket | Used in |
|---|---|---|
| `resolving-merge-conflicts` | `engineering`; in the plugin; same words (one em-dash → comma) | M17 |
| `ask-matt` | `engineering`; in the plugin; **rewritten 2026-08-05**: smart zone ~150k (was ~120k), "Crossing sessions" → "Phase boundaries" (`/compact` the default, `/handoff` narrow), `resolving-merge-conflicts` now listed under Standalone | M18 |
| `wayfinder` | `engineering`; in the plugin; description says "decision tickets" since 2026-07-13 (installed: "investigation tickets") and lost its em-dashes 2026-08-19 | M18 |
| `request-refactor-plan` | **none — removed upstream 2026-08-05** (commit `c66bdee`, replaced by `/to-spec` + `/improve-codebase-architecture`); never in the plugin; still installed here and quoted from the installed file | M18 |
| `grill-me` (delegates to `grilling`) | `productivity`; in the plugin; body now "Call the Skill tool with “grilling”." (2026-08-15); `grilling` itself rewritten into rounds 2026-07-13 → 2026-08-20 | M18 |
| `tdd` (+ `tests.md`, `mocking.md`) | `engineering`; in the plugin; description unchanged | M18 |
| `handoff` | `productivity`; in the plugin; description unchanged (one body line reworded 2026-08-15) | M18 |
| `git-guardrails-claude-code` (+ `scripts/block-dangerous-git.sh`) | `misc` — "Tools I keep around but rarely use, not promoted in the plugin"; **not in the plugin**; description unchanged | M18 |
| `qa` | **none — removed upstream 2026-08-05** with `request-refactor-plan` (replaced by `/triage` + `/to-tickets`); never in the plugin; still installed here | M05 (named), M24 (primary source) |

## Tier 4 — Linear official

| Resource | URL | Used in |
|---|---|---|
| GitHub integration — branch-name linking, Branch format, magic words, the squash-merge FAQ | https://linear.app/docs/github | M12, M13, M34 |
| Pricing (plan gates) — Issue sync is a Core feature on every plan; parsed at cell level 2026-09-13, see `NOTES.md` | https://linear.app/pricing | M12 |
| GitHub Issues Importer (historical issues; sync is forward-only) | https://linear.app/docs/github-to-linear | M12 (learn more) |

## Non-GitHub references used on Week 1 and Week 3 pages

| Resource | URL | Used in |
|---|---|---|
| Git reference: `git merge-base`, `git diff`, `gitrevisions` | https://git-scm.com/docs/git-diff | M03 |
| Pro Git, ch. 3.2 Basic Branching and Merging | https://git-scm.com/book/en/v2/Git-Branching-Basic-Branching-and-Merging | M03, M17 (learn more) |
| git-merge — "How conflicts are presented", "How to resolve conflicts" | https://git-scm.com/docs/git-merge | M16, M17 |
| git-rerere | https://git-scm.com/docs/git-rerere | M17 (learn more) |
| jq manual (moved from `jqlang.github.io`; old address redirects) | https://jqlang.org/manual/ | M04, M06 (learn more) |
| Mermaid: flowchart syntax (`graph LR`, `subgraph`) | https://mermaid.js.org/syntax/flowchart.html | M11 (learn more) |

## Ancillary

Used only where no primary source covers the ground, and always marked as practitioner
material on the page:

- Stacked-PR practice writing (vendor blogs) — M16. Treat claims about tooling as
  marketing; the mechanics come from GitHub's base-branch docs.
- Diff-reviewability heuristics — M14. No authoritative source exists; this is a course
  exercise built on the cohort's own PRs.
  The one practitioner source quoted, marked ancillary on the page:
  [Google eng-practices: Small CLs](https://google.github.io/eng-practices/review/developer/small-cls.html)
  (fetched 2026-09-13).

## Deliberately rejected

- **Anthropic Code Review (managed product)** — requires a Claude Team/Enterprise
  subscription and costs $15–25 per review. Students are on Pro. See `NOTES.md`.
- **GitHub Projects v2** — Linear occupies the PM role; see `MISSION.md` out-of-scope.
- **Dependabot / dependency graph / SBOM** — "dependency" in this course means *work*
  dependency. See `CONTEXT.md`.
