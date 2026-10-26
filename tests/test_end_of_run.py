"""The run ends after five days, and the scoreboard adds up (CT05, CT R4)."""

import logic

POMODORO = "Iconic Pomodoro"
ARRABBIATA = "Drunken Arrabbiata"
CARBOBORA = "Carbobora"

ONE_OF_EACH = {POMODORO: 1, ARRABBIATA: 1, CARBOBORA: 1}
# Buying one of each costs 27.00, selling all three brings in 38.80.
PROFIT_A_DAY = 11.80


def play_five_days(game):
    for _ in range(logic.TOTAL_DAYS):
        game.place_order(ONE_OF_EACH)
        game.open_the_restaurant()


def test_the_run_ends_after_the_fifth_day(fresh_run):
    assert logic.run_is_over() is False

    play_five_days(logic)

    assert logic.current_day() == 6
    assert logic.run_is_over() is True


def test_a_sixth_day_is_refused(fresh_run):
    """CT05: trading stops. Nothing is written when it is tried anyway."""
    play_five_days(logic)
    cash_before = logic.current_cash()

    refused = logic.open_the_restaurant()

    assert refused["ok"] is False
    assert refused["error"] == logic.RUN_IS_OVER
    assert logic.current_cash() == cash_before
    assert logic.current_day() == 6
    assert len(logic.history()) == 5


def test_buying_stops_too(fresh_run):
    """CT05: buying stops as well, not only trading."""
    play_five_days(logic)
    cash_before = logic.current_cash()

    assert logic.place_order({POMODORO: 1}) is None
    assert logic.current_cash() == cash_before
    assert logic.current_stock()[POMODORO] == 0


def test_the_scoreboard_adds_up(fresh_run):
    """Five quiet days: 11.80 profit each, nothing left over."""
    play_five_days(logic)

    result = logic.final_result()

    assert len(result["days"]) == 5
    assert result["days"][0]["sold"] == 3
    assert result["days"][0]["profit"] == PROFIT_A_DAY
    assert result["sold"] == 15
    assert result["profit"] == round(5 * PROFIT_A_DAY, 2)
    assert result["cash"] == 159.00
    assert result["stock_value"] == 0.00
    assert result["gain"] == 59.00

    # With nothing left in the kitchen, the gain is exactly the profit earned.
    assert result["gain"] == result["profit"]


def test_each_dish_is_counted_on_its_own(fresh_run):
    play_five_days(logic)

    dishes = logic.final_result()["dishes"]

    assert dishes[POMODORO]["sold"] == 5
    assert dishes[POMODORO]["revenue"] == 59.50       # 5 x 11.90
    assert dishes[POMODORO]["profit"] == 24.50        # 5 x (11.90 - 7.00)
    assert dishes[CARBOBORA]["profit"] == 15.00       # 5 x (14.00 - 11.00)


def test_leftover_stock_is_still_worth_money(fresh_run):
    """CT R4: unsold stock counts at purchase cost, it is not written off."""
    logic.place_order({POMODORO: 12})                 # 84.00, demand is only 10
    logic.open_the_restaurant()

    assert logic.current_stock()[POMODORO] == 2
    assert logic.stock_value() == 14.00               # 2 x 7.00

    result = logic.final_result()
    assert result["gain"] == round(result["cash"] + 14.00 - 100.00, 2)


def test_starting_over_wipes_everything(fresh_run):
    play_five_days(logic)

    logic.start_new_run()

    assert logic.current_day() == 1
    assert logic.current_cash() == 100.00
    assert logic.history() == []
    assert logic.run_is_over() is False
    assert logic.current_stock() == {POMODORO: 0, ARRABBIATA: 0, CARBOBORA: 0}


def test_leftovers_are_listed_dish_by_dish(fresh_run):
    """The end screen needs to name what is left, not only what it is worth.

    Buying 14 of anything on day one is the most a EUR 100 till allows, so the
    kitchen has to earn its way up before it can overbuy two dishes at once.
    """
    for _ in range(3):
        logic.place_order({POMODORO: 10})      # 70.00, all ten sell
        logic.open_the_restaurant()
    assert logic.current_cash() == 247.00

    logic.place_order({POMODORO: 14, CARBOBORA: 11})   # 98.00 + 121.00
    logic.open_the_restaurant()                        # demand is 10 of each

    left = logic.leftovers()

    assert len(left) == 2
    assert left[0] == {"name": POMODORO, "portions": 4, "value": 28.00}
    assert left[1] == {"name": CARBOBORA, "portions": 1, "value": 11.00}
    assert logic.stock_value() == 39.00


def test_an_empty_kitchen_lists_nothing(fresh_run):
    logic.place_order({POMODORO: 3})
    logic.open_the_restaurant()

    assert logic.leftovers() == []
    assert logic.stock_value() == 0.00
