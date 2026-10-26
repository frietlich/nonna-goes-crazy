"""SQLite storage for Nonna Goes Crazy.

The database file is the game. It is not in the repository (see .gitignore),
so everything here has to be able to build itself from nothing: a fresh clone
has to start.

Only two things ever write: an accepted order, and a completed day. Both write
immediately, so there is no save step and nothing to lose.
"""

import sqlite3
from pathlib import Path

# Where the game lives. The tests point this somewhere temporary.
DB_PATH = Path(__file__).parent / "nonna.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS run (
    id    INTEGER PRIMARY KEY CHECK (id = 1),
    cash  REAL    NOT NULL,
    day   INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS stock (
    dish      TEXT    PRIMARY KEY,
    portions  INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS history (
    day         INTEGER PRIMARY KEY,
    cash_after  REAL    NOT NULL,
    cash_delta  REAL    NOT NULL
);

CREATE TABLE IF NOT EXISTS history_lines (
    day           INTEGER NOT NULL,
    dish          TEXT    NOT NULL,
    stock_before  INTEGER NOT NULL,
    sold          INTEGER NOT NULL,
    revenue       REAL    NOT NULL,
    cogs          REAL    NOT NULL,
    profit        REAL    NOT NULL,
    stock_after   INTEGER NOT NULL,
    PRIMARY KEY (day, dish)
);
"""

_connection = None


def connect():
    """Return the open connection, opening one the first time it is asked for."""
    global _connection
    if _connection is None:
        # check_same_thread=False because Streamlit runs the script in a different
        # thread on every interaction. Only one run happens at a time, so the
        # connection is never used by two of them at once.
        _connection = sqlite3.connect(DB_PATH, check_same_thread=False)
        _connection.row_factory = sqlite3.Row
    return _connection


def close():
    """Drop the connection. The next read opens the file again from scratch."""
    global _connection
    if _connection is not None:
        _connection.close()
        _connection = None


def set_up(dishes, starting_cash):
    """Create the tables, and the opening position if there is no game yet."""
    connection = connect()
    connection.executescript(SCHEMA)
    with connection:
        connection.execute(
            "INSERT OR IGNORE INTO run (id, cash, day) VALUES (1, ?, 1)",
            (starting_cash,),
        )
        for dish in dishes:
            connection.execute(
                "INSERT OR IGNORE INTO stock (dish, portions) VALUES (?, 0)",
                (dish,),
            )


def get_cash():
    row = connect().execute("SELECT cash FROM run WHERE id = 1").fetchone()
    return row["cash"]


def get_day():
    row = connect().execute("SELECT day FROM run WHERE id = 1").fetchone()
    return row["day"]


def get_stock():
    """Return {dish name: portions} for every dish on the menu."""
    rows = connect().execute("SELECT dish, portions FROM stock").fetchall()
    return {row["dish"]: row["portions"] for row in rows}


def save_order(cash_after, portions_after):
    """Write an accepted order: cash down and stock up, in one go."""
    connection = connect()
    with connection:
        connection.execute("UPDATE run SET cash = ? WHERE id = 1", (cash_after,))
        for dish, portions in portions_after.items():
            connection.execute(
                "UPDATE stock SET portions = ? WHERE dish = ?", (portions, dish)
            )


def save_day(day, lines, cash_after, cash_delta, portions_after):
    """Write one completed day: the history entry, the new cash and the new stock.

    All of it in a single transaction, so a day can never be half recorded.
    """
    connection = connect()
    with connection:
        connection.execute(
            "INSERT INTO history (day, cash_after, cash_delta) VALUES (?, ?, ?)",
            (day, cash_after, cash_delta),
        )
        for dish, line in lines.items():
            connection.execute(
                """INSERT INTO history_lines
                   (day, dish, stock_before, sold, revenue, cogs, profit, stock_after)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    day,
                    dish,
                    line["stock_before"],
                    line["sold"],
                    line["revenue"],
                    line["cogs"],
                    line["profit"],
                    line["stock_after"],
                ),
            )
        connection.execute(
            "UPDATE run SET cash = ?, day = ? WHERE id = 1", (cash_after, day + 1)
        )
        for dish, portions in portions_after.items():
            connection.execute(
                "UPDATE stock SET portions = ? WHERE dish = ?", (portions, dish)
            )


def wipe():
    """Throw the whole run away. The tables stay, the rows go."""
    connection = connect()
    with connection:
        connection.execute("DELETE FROM history_lines")
        connection.execute("DELETE FROM history")
        connection.execute("DELETE FROM stock")
        connection.execute("DELETE FROM run")


def get_history():
    """Return every completed day, oldest first, each with its per-dish lines."""
    connection = connect()
    days = connection.execute("SELECT * FROM history ORDER BY day").fetchall()
    history = []
    for day in days:
        lines = connection.execute(
            "SELECT * FROM history_lines WHERE day = ?", (day["day"],)
        ).fetchall()
        history.append(
            {
                "day": day["day"],
                "cash_after": day["cash_after"],
                "cash_delta": day["cash_delta"],
                "dishes": {line["dish"]: dict(line) for line in lines},
            }
        )
    return history
