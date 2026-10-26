"""Start over: throw the game away and begin a new five-day run.

    uv run python seed.py
"""

import db
import logic

if db.DB_PATH.exists():
    db.close()
    db.DB_PATH.unlink()
    print("deleted " + str(db.DB_PATH))

logic.start_up()
print("New run ready: day 1, " + format(logic.STARTING_CASH, ".2f") + " euros, empty kitchen.")
