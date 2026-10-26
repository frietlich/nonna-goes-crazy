"""Money is always rounded to the cent (CT R3).

Plain floating point drifts: EUR 100.00 run through five days of buying one of
each dish and selling them lands on 135.39999999999998 after day three. Rounding
at every step keeps that from ever building up.
"""

import logic

POMODORO = "Iconic Pomodoro"
ARRABBIATA = "Drunken Arrabbiata"
CARBOBORA = "Carbobora"


def test_money_is_rounded_to_the_cent():
    assert logic.money(135.39999999999998) == 135.40
    assert logic.money(0.1 + 0.2) == 0.30
    assert logic.money(119.00000000000001) == 119.00


def test_cash_never_drifts_over_a_whole_run(fresh_run):
    """Five days of buying one of each dish and selling all three.

    Each day costs 27.00 and brings in 38.80, so cash climbs by 11.80 a day.
    """
    for day in range(5):
        logic.place_order({POMODORO: 1, ARRABBIATA: 1, CARBOBORA: 1})
        logic.open_the_restaurant()

    assert logic.current_cash() == 159.00


def test_every_cash_figure_has_at_most_two_decimals(fresh_run):
    """Not just the end: no reading along the way is allowed to be ragged."""
    for day in range(5):
        logic.place_order({POMODORO: 1, ARRABBIATA: 1, CARBOBORA: 1})
        cash = logic.current_cash()
        assert cash == round(cash, 2), f"ragged cash after ordering on day {day + 1}"

        logic.open_the_restaurant()
        cash = logic.current_cash()
        assert cash == round(cash, 2), f"ragged cash after trading on day {day + 1}"


def test_cash_never_goes_negative(fresh_run):
    """CT R3. The till is the limit, and it is checked in the logic.

    The screen greys the button out, but the rule cannot live only there:
    a call that goes past the screen has to be refused just the same.
    """
    assert logic.place_order({POMODORO: 20}) is None       # 140.00
    assert logic.current_cash() == 100.00

    assert logic.place_order({POMODORO: 15}) is None       # 105.00
    assert logic.current_cash() == 100.00

    assert logic.place_order({POMODORO: 14}) == 98.00      # fits, just
    assert logic.current_cash() == 2.00

    refused = logic.buy_and_open({POMODORO: 10000})
    assert refused["error"] == logic.CANNOT_AFFORD
    assert logic.current_cash() == 2.00


def test_a_trading_day_can_only_add_to_the_till(fresh_run):
    """Selling brings money in; there are no running costs in this release."""
    logic.place_order({POMODORO: 10})
    before = logic.current_cash()

    logic.open_the_restaurant()

    assert logic.current_cash() > before


def test_stock_never_goes_negative_either(fresh_run):
    """CT R3 names stock next to cash."""
    logic.buy_and_open({POMODORO: 3})               # demand 10, only 3 to sell
    assert logic.current_stock()[POMODORO] == 0

    logic.place_order({ARRABBIATA: 1})
    logic.open_the_restaurant()                     # Pomodoro has nothing left

    for portions in logic.current_stock().values():
        assert portions >= 0
