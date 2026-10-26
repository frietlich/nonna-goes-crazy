"""Setting the selling price, and what the demand rule does with it (CT03, CT R1).

Iconic Pomodoro costs 7.00 and has a reference price of 11.90, so twice the
reference is 23.80. Those three numbers decide every case below.
"""

import db
import logic

POMODORO = "Iconic Pomodoro"
ARRABBIATA = "Drunken Arrabbiata"
CARBOBORA = "Carbobora"


def test_a_new_run_charges_the_reference_price(fresh_run):
    assert logic.current_prices() == {
        POMODORO: 11.90,
        ARRABBIATA: 12.90,
        CARBOBORA: 14.00,
    }


def test_at_the_reference_price_everyone_comes(fresh_run):
    """Ten portions wanted, ten in the kitchen, ten sold."""
    day = logic.buy_and_open({POMODORO: 10}, {POMODORO: 11.90})

    sold = day["dishes"][POMODORO]
    assert sold["price"] == 11.90
    assert sold["sold"] == 10
    assert sold["revenue"] == 119.00
    assert logic.current_cash() == 149.00


def test_asking_more_than_the_reference_halves_the_room(fresh_run):
    """Above the reference up to twice it, demand drops to five (CT R1)."""
    day = logic.buy_and_open({POMODORO: 10}, {POMODORO: 15.00})

    sold = day["dishes"][POMODORO]
    assert sold["sold"] == 5
    assert sold["revenue"] == 75.00          # 5 x 15.00
    assert sold["cogs"] == 35.00             # 5 x 7.00
    assert sold["profit"] == 40.00
    assert sold["stock_after"] == 5
    assert logic.current_cash() == 105.00    # 100 - 70 + 75


def test_asking_more_than_twice_the_reference_empties_it(fresh_run):
    """Above twice the reference nobody comes at all, and the food stays."""
    day = logic.buy_and_open({POMODORO: 10}, {POMODORO: 24.00})

    sold = day["dishes"][POMODORO]
    assert sold["sold"] == 0
    assert sold["revenue"] == 0.00
    assert logic.current_cash() == 30.00     # only the 70.00 of shopping left
    assert logic.current_stock()[POMODORO] == 10


def test_the_boundaries_are_where_the_brief_says(fresh_run):
    """A2, now reachable by clicking: 11.90, 11.91, 23.80 and 23.81."""
    pomodoro = logic.find_dish(POMODORO)

    assert logic.demand_for(pomodoro, 11.90) == 10
    assert logic.demand_for(pomodoro, 11.91) == 5
    assert logic.demand_for(pomodoro, 23.80) == 5
    assert logic.demand_for(pomodoro, 23.81) == 0


def test_a_price_of_zero_or_less_is_refused(fresh_run):
    """A2: and nothing is written, so half the menu cannot end up changed."""
    assert logic.set_prices({POMODORO: 0.00}) is False
    assert logic.set_prices({POMODORO: -5.00}) is False
    assert logic.current_prices()[POMODORO] == 11.90

    refused = logic.buy_and_open({POMODORO: 10}, {POMODORO: 0.00})

    assert refused["ok"] is False
    assert refused["error"] == logic.BAD_PRICE
    assert logic.current_cash() == 100.00
    assert logic.current_stock()[POMODORO] == 0
    assert logic.current_day() == 1


def test_one_bad_price_leaves_the_others_alone(fresh_run):
    """All or nothing: a wrong entry anywhere stops the whole set."""
    assert logic.set_prices({POMODORO: 13.00, CARBOBORA: -1.00}) is False

    assert logic.current_prices()[POMODORO] == 11.90
    assert logic.current_prices()[CARBOBORA] == 14.00


def test_yesterdays_price_is_still_there_today(fresh_run):
    """Chosen on purpose, so it stays until it is changed."""
    logic.buy_and_open({POMODORO: 10}, {POMODORO: 15.00})

    assert logic.current_prices()[POMODORO] == 15.00

    logic.buy_and_open({POMODORO: 10})       # no prices passed at all
    assert logic.current_prices()[POMODORO] == 15.00


def test_prices_survive_a_restart(fresh_run):
    """A5 names prices next to cash, stock and history."""
    logic.set_prices({POMODORO: 15.00, ARRABBIATA: 20.00, CARBOBORA: 9.50})

    db.close()

    assert logic.current_prices() == {
        POMODORO: 15.00,
        ARRABBIATA: 20.00,
        CARBOBORA: 9.50,
    }


def test_the_history_remembers_what_was_charged(fresh_run):
    """The day's report shows the price next to the result, so it is stored."""
    logic.buy_and_open({POMODORO: 10}, {POMODORO: 15.00})

    line = logic.history()[0]["dishes"][POMODORO]
    assert line["price"] == 15.00
    assert line["sold"] == 5
