# The Seed Repo is Python, not TypeScript

The repo owner's default convention is TypeScript for web and app builds. The Seed Repo
(`flashcards-seed`) is Python with pytest and ruff instead.

The cohort's fluency is closer to Python than to the Node/TypeScript ecosystem, and in
this course the application's language is a *substrate*, not a subject — students direct
Claude to write the code, and are assessed on the workflow around the diff rather than on
the diff's syntax. Choosing the language the cohort reads most fluently lowers the cost of
the only part that must be read closely: reviewing a diff for a planted bug.

Consequences:

- `setup-pre-commit` (Husky + lint-staged) does not apply. The Python `pre-commit`
  framework is configured directly in the Seed Repo instead, and the skill is named in the
  Week 3 toolbelt lesson as Node-specific rather than demonstrated.
- CI is pytest + ruff. The pinned interpreter is chosen for settled wheel availability,
  **not** the newest release — the local machine runs 3.14.4, which is ahead of where CI
  should sit. Fast CI matters here: the required-status-check and merge-queue lessons in
  Week 5 stall if a run takes minutes.
- The domain layer is an SM-2 spaced-repetition scheduler. Interval and ease-factor
  arithmetic is where the course's planted review bugs live, because such bugs survive
  naive tests and must be caught by reading.
