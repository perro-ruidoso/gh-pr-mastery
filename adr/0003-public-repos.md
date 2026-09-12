# All course repos are public

**Status:** accepted. Reasoning revised 2026-09-12 after the course org was created and its
plan checked; the decision is unchanged, but two of its three original premises were wrong.

## What was originally assumed

That the course org would be on **GitHub Free**, where branch restrictions and rulesets
apply to public repositories only. That made "public" follow from three independent
constraints.

## What is actually true

The org `perro-ruidoso` was created on 2026-09-12 and reports:

```
$ gh api orgs/perro-ruidoso --jq '.plan'
{"name":"team","seats":2,"filled_seats":1,"private_repos":999999,"space":976562499}
```

It is on **GitHub Team**, not Free. That changes the picture:

| Gate | On Team, private repo | On Team, public repo |
|---|---|---|
| Branch protection / rulesets | ✅ available | ✅ available |
| Required status checks, required reviews, conversation resolution | ✅ available | ✅ available |
| **Merge queue** | ❌ Enterprise Cloud only | ✅ available |
| Actions minutes | billed against the org's allowance | free |

So two of the original three reasons evaporated. Rulesets and branch protection would work
fine on private repos now.

## The decision, and the one reason that survives

**All course repos stay public.**

Merge queue is the load-bearing reason. Verified against GitHub's documentation (quotes and
links in `NOTES.md`): merge queue is available in "any public repository owned by an
organization," and for private repositories requires GitHub Enterprise Cloud — it is *not*
available on Team. M29 asks students to enable and use one, so a private repo puts that
objective out of reach at any plan tier short of Enterprise.

Free Actions minutes on public repositories are a real secondary benefit: Week 5 has
students re-running CI repeatedly while they get a ruleset right, and on private repos that
would consume a metered allowance shared across the whole cohort.

## Consequences and accepted risks

- Student work is world-readable. This must be stated in the syllabus before enrolment, and
  it appears in a callout on the Course Home page and in M01.
- Nothing personal goes in these repos. The flashcards domain was chosen partly for this.
- **Team is a paid plan.** At the time of writing the org has 2 seats with 1 filled. A
  cohort of 8–14 students plus the instructor needs 9–15 seats. Whether to pay for that or
  downgrade to Free is an open question in `NOTES.md` — note that **downgrading to Free
  costs this course nothing**, because every gate the curriculum actually uses works on a
  public repository at either tier.

## Alternatives rejected

- **Private repos on Team** — buys privacy, loses M29 (merge queue). Rejected.
- **Enterprise Cloud** — would allow private repos with merge queue, at a price far beyond
  what a course justifies. Rejected.
