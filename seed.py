"""Start over: throw the run away and begin a new five-day run.

    uv run python seed.py

This empties the tables rather than deleting the database file. Deleting the
file pulls it out from under any app that is already running: the open
connection still points at the file that was removed, and the next write fails
with "attempt to write a readonly database". Emptying the rows leaves the file
where it is, so a running app simply finds a fresh game.
"""

import db
import logic

logic.start_up()          # make sure the tables exist at all
db.wipe()
logic.start_up()          # and put the opening position back

print(
    "New run ready: day 1, "
    + format(logic.STARTING_CASH, ".2f")
    + " euros, empty kitchen."
)
