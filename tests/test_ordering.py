"""Ordering ingredients: the accepted action, and the order that cannot be paid for.

Numbers come from specs/first-feature.md, checks 1 and 2.
"""

import logic

POMODORO = "Iconic Pomodoro"
ARRABBIATA = "Drunken Arrabbiata"
CARBOBORA = "Carbobora"


def test_a_new_game_starts_with_100_euros_and_an_empty_kitchen(fresh_run):
    assert logic.current_cash() == 100.00
    assert logic.current_day() == 1
    assert logic.current_stock() == {POMODORO: 0, ARRABBIATA: 0, CARBOBORA: 0}
    assert logic.history() == []


def test_an_order_moves_cash_and_stock_together(fresh_run):
    """Check 1: ordering 10 Pomodoro costs EUR 70.00 and leaves EUR 30.00."""
    logic.place_order({POMODORO: 10})

    assert logic.current_cash() == 30.00
    assert logic.current_stock()[POMODORO] == 10


def test_ordering_does_not_cost_a_day(fresh_run):
    """Shopping costs money, not time: no day advance, no history entry."""
    logic.place_order({POMODORO: 10})

    assert logic.current_day() == 1
    assert logic.history() == []


def test_the_total_adds_up_the_whole_order(fresh_run):
    """One of each: 7.00 + 9.00 + 11.00."""
    total = logic.order_total({POMODORO: 1, ARRABBIATA: 1, CARBOBORA: 1})

    assert total == 27.00


def test_an_order_that_costs_too_much_is_not_affordable(fresh_run):
    """Check 2: with EUR 30.00, five Pomodoro cost EUR 35.00 and four cost EUR 28.00."""
    logic.place_order({POMODORO: 10})          # EUR 100.00 -> EUR 30.00

    assert logic.order_total({POMODORO: 5}) == 35.00
    assert logic.can_afford({POMODORO: 5}) is False

    assert logic.order_total({POMODORO: 4}) == 28.00
    assert logic.can_afford({POMODORO: 4}) is True


def test_an_empty_order_is_not_worth_placing(fresh_run):
    """Nothing to order: the button has nothing to do."""
    assert logic.order_total({}) == 0.00
    assert logic.order_total({POMODORO: 0, ARRABBIATA: 0, CARBOBORA: 0}) == 0.00
