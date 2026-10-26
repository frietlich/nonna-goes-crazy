"""The three requirements that were only half done, and the rounding (CT01, CT04, A6, CT R3)."""

import logic

POMODORO = "Iconic Pomodoro"
ARRABBIATA = "Drunken Arrabbiata"
CARBOBORA = "Carbobora"


def test_money_rounds_a_half_up_like_money_does(fresh_run):
    """CT R3. Python's own round() sends a half to the nearest even number,
    so 2.675 would become 2.67. Nobody hands back 2.67 for two sixty-seven
    and a half."""
    assert logic.money(2.675) == 2.68
    assert logic.money(1.005) == 1.01
    assert logic.money(0.125) == 0.13
    assert logic.money(2.665) == 2.67          # genuinely rounds down
    assert logic.money(119.00000000000001) == 119.00


def test_a_day_reports_its_totals_as_well(fresh_run):
    """CT04 asks for sold, revenue, cost of goods and profit in total,
    not only dish by dish."""
    # 10 + 4 would cost 106.00 and the till holds 100.00, so three it is.
    day = logic.buy_and_open({POMODORO: 10, ARRABBIATA: 3})

    assert day["sold"] == 13                   # both lots are under the demand of 10
    assert day["revenue"] == 157.70            # 10 x 11.90 + 3 x 12.90
    assert day["cogs"] == 97.00                # 10 x 7.00 + 3 x 9.00
    assert day["profit"] == 60.70


def test_the_totals_match_the_dishes_added_up(fresh_run):
    """Whatever the table shows per dish has to add up to the total line."""
    day = logic.buy_and_open({POMODORO: 6, ARRABBIATA: 3, CARBOBORA: 2})

    assert day["sold"] == sum(l["sold"] for l in day["dishes"].values())
    assert day["revenue"] == logic.money(sum(l["revenue"] for l in day["dishes"].values()))
    assert day["cogs"] == logic.money(sum(l["cogs"] for l in day["dishes"].values()))
    assert day["profit"] == logic.money(sum(l["profit"] for l in day["dishes"].values()))


def test_a_brand_new_run_has_not_started_yet(fresh_run):
    """CT01, A6: the menu offers "start" and never asks to confirm deleting nothing."""
    assert logic.run_has_started() is False


def test_buying_alone_counts_as_a_started_run(fresh_run):
    """Money spent is progress, even before a single day is served."""
    logic.place_order({POMODORO: 1})

    assert logic.run_has_started() is True


def test_a_played_day_counts_as_a_started_run(fresh_run):
    logic.buy_and_open({POMODORO: 5})

    assert logic.run_has_started() is True


def test_starting_over_makes_it_unstarted_again(fresh_run):
    """A6: a confirmed new run restores day one, EUR 100 and an empty history."""
    logic.buy_and_open({POMODORO: 5})

    logic.start_new_run()

    assert logic.run_has_started() is False
    assert logic.current_day() == 1
    assert logic.current_cash() == 100.00
    assert logic.history() == []
