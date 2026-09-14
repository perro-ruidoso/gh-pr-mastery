"""Domain layer: the SM-2 scheduler."""

from __future__ import annotations

from datetime import date

import pytest

from flashcards.domain.scheduler import ReviewState, review

TODAY = date(2026, 9, 14)


def test_review_returns_a_new_state_and_leaves_the_old_one_alone() -> None:
    before = ReviewState()
    after = review(before, 5, TODAY)
    assert after is not before
    assert (before.repetitions, before.ease_factor, before.interval) == (0, 2.5, 0)


def test_first_success_schedules_one_day_out() -> None:
    after = review(ReviewState(), 4, TODAY)
    assert (after.repetitions, after.interval) == (1, 1)
    assert after.due == date(2026, 9, 15)


def test_second_success_schedules_six_days_out() -> None:
    once = review(ReviewState(), 4, TODAY)
    twice = review(once, 4, date(2026, 9, 15))
    assert (twice.repetitions, twice.interval) == (2, 6)


def test_third_success_multiplies_the_previous_interval_by_the_ease_factor() -> None:
    state = ReviewState(repetitions=2, ease_factor=2.5, interval=6)
    after = review(state, 4, TODAY)  # grade 4 leaves the ease factor at 2.5
    assert (after.repetitions, after.ease_factor, after.interval) == (3, 2.5, 15)


def test_perfect_grade_raises_the_ease_factor_by_a_tenth() -> None:
    assert review(ReviewState(), 5, TODAY).ease_factor == pytest.approx(2.6)


def test_ease_factor_never_drops_below_the_floor() -> None:
    state = ReviewState(repetitions=1, ease_factor=1.3, interval=1)
    assert review(state, 5, TODAY).ease_factor == pytest.approx(1.4)


def test_failure_restarts_the_card_from_scratch() -> None:
    after = review(ReviewState(repetitions=3, interval=15), 1, TODAY)
    assert (after.repetitions, after.interval) == (0, 1)
    assert after.ease_factor == 2.5  # "as if the item was memorized anew"
    assert after.due == date(2026, 9, 15)


def test_later_intervals_are_whole_days() -> None:
    after = review(ReviewState(repetitions=3, ease_factor=2.36, interval=15), 4, TODAY)
    assert after.interval == 35  # 15 * 2.36 = 35.4
    assert isinstance(after.interval, int)


@pytest.mark.parametrize("grade", [-1, 6, 42])
def test_grade_outside_zero_to_five_is_rejected(grade: int) -> None:
    with pytest.raises(ValueError, match="between 0 and 5"):
        review(ReviewState(), grade, TODAY)
