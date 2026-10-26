"""Opening the restaurant: the day that reconciles, and the day that is refused.

Numbers come from specs/first-feature.md, checks 3 to 7.
"""

import logic

POMODORO = "Iconic Pomodoro"
ARRABBIATA = "Drunken Arrabbiata"
CARBOBORA = "Carbobora"


def test_demand_sits_on_the_right_side_of_every_boundary():
    """Check 7, CT R1. Pomodoro's reference price is 11.90, twice that is 23.80.

    Logic only: with prices fixed at the reference price, the app never charges
    anything else, so this cannot be reached by clicking.
    """
    pomodoro = logic.find_dish(POMODORO)

    assert logic.demand_for(pomodoro, 11.90) == 10
    assert logic.demand_for(pomodoro, 11.91) == 5
    assert logic.demand_for(pomodoro, 23.80) == 5
    assert logic.demand_for(pomodoro, 23.81) == 0


def test_a_trading_day_reconciles(fresh_run):
    """Check 4: 10 Pomodoro at 11.90 -> revenue 119.00, cogs 70.00, profit 49.00."""
    logic.place_order({POMODORO: 10})          # EUR 30.00 left, 10 portions

    day = logic.open_the_restaurant()

    sold = day["dishes"][POMODORO]
    assert sold["stock_before"] == 10
    assert sold["sold"] == 10
    assert sold["revenue"] == 119.00
    assert sold["cogs"] == 70.00
    assert sold["profit"] == 49.00
    assert sold["stock_after"] == 0

    assert day["cash_after"] == 149.00
    assert day["cash_delta"] == 119.00
    assert logic.current_cash() == 149.00
    assert logic.current_stock()[POMODORO] == 0
    assert logic.current_day() == 2
    assert len(logic.history()) == 1


def test_stock_limits_sales(fresh_run):
    """Check 5: three in the kitchen and demand of ten sells three, never more."""
    logic.place_order({POMODORO: 3})

    day = logic.open_the_restaurant()

    assert day["dishes"][POMODORO]["sold"] == 3
    assert logic.current_stock()[POMODORO] == 0


def test_a_dish_with_no_stock_sells_nothing(fresh_run):
    """Check 5, second half: zero stock sells zero and never goes below."""
    logic.place_order({POMODORO: 3})

    day = logic.open_the_restaurant()

    assert day["dishes"][ARRABBIATA]["sold"] == 0
    assert logic.current_stock()[ARRABBIATA] == 0


def test_opening_an_empty_kitchen_is_refused(fresh_run):
    """Check 3: the one rule. Nothing is written when it fires."""
    assert logic.kitchen_is_empty() is True

    refused = logic.open_the_restaurant()

    assert refused["ok"] is False
    assert refused["error"] == logic.KITCHEN_IS_EMPTY
    assert logic.current_cash() == 100.00
    assert logic.current_day() == 1
    assert logic.current_stock() == {POMODORO: 0, ARRABBIATA: 0, CARBOBORA: 0}
    assert logic.history() == []


def test_no_order_is_needed_when_stock_remains(fresh_run):
    """Check 6: leftovers carry forward, so day two opens without shopping."""
    logic.place_order({POMODORO: 14})          # more than the demand of 10

    logic.open_the_restaurant()                # sells 10, leaves 4
    assert logic.current_stock()[POMODORO] == 4

    second = logic.open_the_restaurant()       # no order in between

    assert second["ok"] is True
    assert second["dishes"][POMODORO]["sold"] == 4
    assert logic.current_day() == 3
    assert len(logic.history()) == 2
