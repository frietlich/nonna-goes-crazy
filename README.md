# Nonna Goes Crazy

Run a pasta restaurant on campus for five days: buy ingredients, set prices,
open for the day, and find out whether you made money. Three dishes on the
menu — Iconic Pomodoro, Drunken Arrabbiata and Carbobora.

Solo project for Introduction to Programming, Nova SBE 2026/27, built against
the Campus Tycoon brief.

## Run it

```
uv run streamlit run app.py
```

The first run downloads Python and the libraries, then opens the app in the
browser. No `uv`? macOS: `curl -LsSf https://astral.sh/uv/install.sh | sh`,
then open a new terminal.

## Tests

```
uv run pytest
```

## Start over

```
uv run python seed.py
```

Deletes the local database and creates a fresh run: day 1, EUR 100, no stock.

## Folder map

```
app.py                  the screens (start here)
logic.py                the rules: demand, sales, money
db.py                   the SQLite database: schema, reading, writing
seed.py                 reset to a fresh run
specs/first-feature.md  what is being built right now
docs/product-brief.md   the business brief the spec comes from
tests/                  one test per Done when line of the spec
AGENTS.md               notes for the coding agent
```

The database file is not in the repository. It is created on first start.
