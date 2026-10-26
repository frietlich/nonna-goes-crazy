# Nonna Goes Crazy — notes for the agent

A pasta restaurant on campus, built against the Campus Tycoon brief. Solo
project for Introduction to Programming, Nova SBE. The person asking is a
**beginner**. Teach, don't just do.

## Running things

- Run the app: `uv run streamlit run app.py` — uv installs Python and the
  libraries by itself. Never use `pip` or `python -m venv`.
- Tests: `uv run pytest`.
- Reset the game: `uv run python seed.py` — drops the local database and
  creates a fresh run (day 1, EUR 100, no stock).

## The project

`app.py` = the screens and the entry point. `logic.py` = the rules: demand,
sales, money. `db.py` = the SQLite database: schema, reading, writing.

The database file is **local state and is not in git** (see `.gitignore`). So
`db.py` has to be able to create the schema and the starting run from nothing,
or a fresh clone cannot start.

`docs/product-brief.md` is the business brief. Rule ids like CT02, CT R1 and
A3 come from there. `specs/first-feature.md` is the task being built.

## How to answer

- Every claim about the code comes with **file and line**. Show the lines;
  don't paraphrase a function that can be read.
- Build each task on a branch named after it, e.g. `first-feature`. Never
  commit to main directly.
- After every change, run the tests for the task and paste the final output.
  The output is the proof, not a sentence.
- **Never weaken, skip or delete a test to make the code pass.** If a test
  looks wrong, check it against `docs/product-brief.md`, say what is wrong and
  stop. Fixing a test means correcting it against the brief, out loud.
- Check before you claim, and check before you create. If you have not seen it
  this minute, say so instead of assuming.
- Money is handled to two decimals (CT R3). Cash and stock never go negative.
- A completed day is recorded once (CT R5). Restarting the app must never
  replay a day. Reloading the browser is not a restart test.
