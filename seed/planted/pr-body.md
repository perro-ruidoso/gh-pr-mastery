## Intent
Land the SM-2 scheduler: `review(state, grade, today)` returns a new `ReviewState` with its repetition count, ease factor, interval, and due date updated, as `docs/adr/0001-sm2-rounding-and-the-clock.md` specifies. Per `CLAUDE.md`, a PR that changes scheduling arithmetic names the ADR rules it implements: **Ease Factor** (update, then the 1.3 floor), **Failure** (a grade below 3 restarts the card), and **Rounding** (whole days, floor of one day).

## Scope
- `src/flashcards/domain/scheduler.py` (new): `ReviewState` and `review`, one function, two constants. Imports nothing from `storage/` or `cli/`.
- `tests/domain/test_scheduler.py` (new): one test per rule.
- **Not touched:** `Card`, the JSON store, the CLI.

## Verification
- `pytest`: the new tests pass with the existing suite; `ruff check .`, `ruff format --check .`, and `mypy` clean.

## Risk
- Low: a pure function with the ADR as its specification and a test per rule. If a reviewer reads a rule differently from the ADR, that is the thing to look at first.

Closes #ISSUE
