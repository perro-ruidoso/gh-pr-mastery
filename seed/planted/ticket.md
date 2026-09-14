## Context

This is the heart of the application: given a card's current review state and the learner's grade, decide when the card is next due. It is specified completely in `docs/adr/0001-sm2-rounding-and-the-clock.md`; implement that, not something like it. Until the review-state fields land on `Card`, the scheduler keeps its state in its own small `ReviewState` beside `Card`.

## Acceptance criteria

- [ ] New module `src/flashcards/domain/scheduler.py`, importing nothing from `storage/` or `cli/`
- [ ] `review(state, grade, today)` returns a **new** state - it never mutates and never reads the clock
- [ ] Intervals follow `I(1)=1`, `I(2)=6`, `I(n)=I(n-1)*EF`, rounded **half-up** with a floor of 1 day; bare `round()` is wrong and `docs/adr/0001` says why
- [ ] The ease factor update is applied first and the 1.3 floor after
- [ ] A grade below 3 resets the repetition count and **leaves the ease factor unchanged**
- [ ] A grade outside 0-5 raises `ValueError`
- [ ] `tests/domain/test_scheduler.py` covers each rule above by name, including a fail-then-recover sequence and an exact-half interval

## Out of scope

Joining `ReviewState` to `Card`, choosing which cards to review, and anything that reads or writes a file.

_Layer: `domain`_
