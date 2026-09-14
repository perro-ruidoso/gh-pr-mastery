"""SM-2 scheduling: the one place the review arithmetic lives.

``review`` takes a ReviewState, the learner's Grade, and ``today``, and returns a
*new* ReviewState. It never reads the clock and never touches a file -- see rule 2
in ``CLAUDE.md`` and ``docs/adr/0001-sm2-rounding-and-the-clock.md``, which this
module implements line by line:

* Ease Factor update first, then the 1.3 floor (never the other way round).
* A failing Grade (below 3) restarts the Repetition count and leaves the Ease
  Factor untouched.
* Intervals are rounded half-up to whole days, never below 1 -- not ``round()``.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import date, timedelta

STARTING_EASE = 2.5
MIN_EASE = 1.3


@dataclass(frozen=True)
class ReviewState:
    """The scheduling half of a Card, kept beside ``Card`` until the two are joined.

    Args:
        repetitions: Consecutive successful reviews so far (the Repetition count).
        ease_factor: The per-card multiplier SM-2 applies to future intervals.
        interval: Whole days until the card is next due.
        due: The date the card is next due, or ``None`` if never reviewed.
    """

    repetitions: int = 0
    ease_factor: float = STARTING_EASE
    interval: int = 0
    due: date | None = None


def review(state: ReviewState, grade: int, today: date) -> ReviewState:
    """Return ``state`` as it should be after grading the card ``grade`` on ``today``.

    Args:
        state: The card's review state before this review.
        grade: The learner's 0-5 Grade for their recall of the card.
        today: The date the review happened; supplied by the caller, never read
            from the clock here.

    Returns:
        A new ReviewState. ``state`` itself is not changed.

    Raises:
        ValueError: If ``grade`` is outside 0-5.
    """
    if not 0 <= grade <= 5:
        raise ValueError(f"Grade must be between 0 and 5, got {grade}")

    # Bounds first, so nothing below can see an out-of-range ease factor.
    ef = max(MIN_EASE, state.ease_factor)

    if grade < 3:
        # SM-2: "start repetitions for the item from the beginning ... as if the
        # item was memorized anew" -- so the card goes back to its starting state.
        reps, ef, interval = 0, STARTING_EASE, 1
    else:
        reps = state.repetitions + 1
        ef = ef + (0.1 - (5 - grade) * (0.08 + (5 - grade) * 0.02))
        interval = (
            1 if reps == 1 else 6 if reps == 2 else max(1, round(state.interval * ef))
        )

    return replace(
        state,
        repetitions=reps,
        ease_factor=ef,
        interval=interval,
        due=today + timedelta(days=interval),
    )
