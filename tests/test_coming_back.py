"""Stopping the app and starting it again. Check 8, and CT R5 / A5.

The point of these tests is that the numbers come out of the database and not
out of memory. Each one writes, throws away every connection and every cached
value, reads again, and compares.
"""

import db
import logic

POMODORO = "Iconic Pomodoro"


def reopen():
    """Forget everything the process is holding and read the database again."""
    db.close()


def test_a_restart_keeps_the_run(fresh_run):
    """Check 8: cash, stock, day and history survive a restart unchanged."""
    logic.place_order({POMODORO: 10})
    logic.open_the_restaurant()

    reopen()

    assert logic.current_cash() == 149.00
    assert logic.current_stock()[POMODORO] == 0
    assert logic.current_day() == 2


def test_a_restart_does_not_replay_the_day(fresh_run):
    """CT R5: reopening the app must not charge yesterday's sales again."""
    logic.place_order({POMODORO: 10})
    logic.open_the_restaurant()

    reopen()
    reopen()                                   # twice, to be sure

    assert len(logic.history()) == 1
    assert logic.history()[0]["day"] == 1
    assert logic.current_cash() == 149.00


def test_an_order_survives_on_its_own(fresh_run):
    """Saved immediately: closing after shopping, before trading, loses nothing."""
    logic.place_order({POMODORO: 10})

    reopen()

    assert logic.current_cash() == 30.00
    assert logic.current_stock()[POMODORO] == 10
    assert logic.current_day() == 1
    assert logic.history() == []


def test_a_refused_opening_writes_nothing_even_across_a_restart(fresh_run):
    """The rule leaves no trace at all, not even one that shows up later."""
    logic.open_the_restaurant()                # refused, kitchen is empty

    reopen()

    assert logic.current_cash() == 100.00
    assert logic.current_day() == 1
    assert logic.history() == []
