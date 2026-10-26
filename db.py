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
    portions  INTEGER NOT NULL,
    price     REAL    NOT NULL DEFAULT 0
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
    price         REAL    NOT NULL DEFAULT 0,
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


def add_missing_column(connection, table, column, definition):
    """Add a column a database made by an earlier version does not have yet.

    The database file lives on one laptop and is never in the repository, so a
    game started before a column existed would otherwise crash on the next
    start. CREATE TABLE IF NOT EXISTS does not reach an existing table.
    """
    present = [row["name"] for row in connection.execute("PRAGMA table_info(" + table + ")")]
    if column not in present:
        connection.execute("ALTER TABLE " + table + " ADD COLUMN " + column + " " + definition)


def set_up(opening_prices, starting_cash):
    """Create the tables, and the opening position if there is no game yet.

    opening_prices is {dish: reference price}: a new run starts by asking the
    reference price for everything, and the owner changes it from there.
    """
    connection = connect()
    connection.executescript(SCHEMA)
    with connection:
        add_missing_column(connection, "stock", "price", "REAL NOT NULL DEFAULT 0")
        add_missing_column(connection, "history_lines", "price", "REAL NOT NULL DEFAULT 0")

        connection.execute(
            "INSERT OR IGNORE INTO run (id, cash, day) VALUES (1, ?, 1)",
            (starting_cash,),
        )
        for dish, price in opening_prices.items():
            connection.execute(
                "INSERT OR IGNORE INTO stock (dish, portions, price) VALUES (?, 0, ?)",
                (dish, price),
            )
            # A database from before prices existed has 0.00 in the column.
            connection.execute(
                "UPDATE stock SET price = ? WHERE dish = ? AND price <= 0",
                (price, dish),
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


def get_prices():
    """Return {dish: the price the owner is charging today}."""
    rows = connect().execute("SELECT dish, price FROM stock").fetchall()
    return {row["dish"]: row["price"] for row in rows}


def save_prices(prices):
    """Write the chosen selling prices. Saved at once, like everything else."""
    connection = connect()
    with connection:
        for dish, price in prices.items():
            connection.execute(
                "UPDATE stock SET price = ? WHERE dish = ?", (price, dish)
            )


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
                   (day, dish, stock_before, sold, revenue, cogs, profit,
                    stock_after, price)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    day,
                    dish,
                    line["stock_before"],
                    line["sold"],
                    line["revenue"],
                    line["cogs"],
                    line["profit"],
                    line["stock_after"],
                    line["price"],
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
