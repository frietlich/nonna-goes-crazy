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
