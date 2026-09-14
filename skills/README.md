# Vendored skills

Skills the course teaches that students cannot get from the `mattpocock/skills` plugin.
Each folder is one skill, byte-identical (line endings aside) to the last upstream copy,
with its origin recorded here. Install one with:

```bash
mkdir -p ~/.claude/skills/qa
curl -fsSL https://raw.githubusercontent.com/perro-ruidoso/gh-pr-mastery/main/skills/qa/SKILL.md \
  -o ~/.claude/skills/qa/SKILL.md
```

| Skill | Origin | Why vendored |
|---|---|---|
| `qa` | `mattpocock/skills`, `skills/deprecated/qa/SKILL.md` at `f958fa1` (the parent of `c66bdee`, which removed it on 2026-08-05); identical to the course machine's 2026-07-09 `npx skills` snapshot. MIT licence (`gh api repos/mattpocock/skills/license`). | M24 teaches filing what review uncovers as issues from a conversation. The plugin never carried `qa`, and the changeset's named replacements (`/triage`, `/to-tickets`) do a different job: triage moves *existing* issues through states, and `to-tickets` decomposes a *spec*. Decided 2026-09-14 (NOTES.md, Week 4; the Weeks 1-3 audit's S3). |

The upstream removal commit's message: "chore: remove six unused skills and the personal
bucket". Re-check before each cohort whether upstream has reintroduced an equivalent; if it
has, prefer the plugin's copy and delete this one.
