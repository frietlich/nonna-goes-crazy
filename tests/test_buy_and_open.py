"""Ordering and opening are one action: set the quantities, open the doors."""

import logic

POMODORO = "Iconic Pomodoro"
ARRABBIATA = "Drunken Arrabbiata"
CARBOBORA = "Carbobora"


def test_what_is_bought_is_sold_the_same_day(fresh_run):
    """The point of putting the two together: no day passes between them."""
    day = logic.buy_and_open({POMODORO: 10})

    assert day["ok"] is True
    assert day["dishes"][POMODORO]["stock_before"] == 10
    assert day["dishes"][POMODORO]["sold"] == 10
    assert logic.current_cash() == 149.00        # 100 - 70 + 119
    assert logic.current_day() == 2


def test_opening_without_buying_works_when_stock_remains(fresh_run):
    """Leftovers carry forward, so an empty order is a fine choice (CT R2)."""
    logic.buy_and_open({POMODORO: 14})           # demand is 10, four stay
    assert logic.current_stock()[POMODORO] == 4

    second = logic.buy_and_open({})

    assert second["ok"] is True
    assert second["dishes"][POMODORO]["sold"] == 4
    assert logic.current_day() == 3


def test_an_empty_order_on_an_empty_kitchen_is_refused(fresh_run):
    """The one rule still bites, and still writes nothing."""
    refused = logic.buy_and_open({})

    assert refused["ok"] is False
    assert refused["error"] == logic.KITCHEN_IS_EMPTY
    assert logic.current_cash() == 100.00
    assert logic.current_day() == 1
    assert logic.history() == []


def test_an_order_that_cannot_be_paid_for_stops_everything(fresh_run):
    """No half action: nothing bought, no day served, not a cent moved."""
    refused = logic.buy_and_open({POMODORO: 20})     # 140.00 against 100.00

    assert refused["ok"] is False
    assert refused["error"] == logic.CANNOT_AFFORD
    assert logic.current_cash() == 100.00
    assert logic.current_stock()[POMODORO] == 0
    assert logic.current_day() == 1
    assert logic.history() == []


def test_nothing_runs_once_the_five_days_are_done(fresh_run):
    for _ in range(logic.TOTAL_DAYS):
        logic.buy_and_open({POMODORO: 1, ARRABBIATA: 1, CARBOBORA: 1})

    refused = logic.buy_and_open({POMODORO: 1})

    assert refused["ok"] is False
    assert refused["error"] == logic.RUN_IS_OVER
    assert logic.current_day() == 6
    assert len(logic.history()) == 5
