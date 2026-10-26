"""Shared test setup: make the app modules importable, and give every test its own database."""

import os
import sys

import pytest

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# So that "import db" and "import logic" work when pytest runs from the project folder.
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

import db       # noqa: E402  (has to come after the path is set up)
import logic    # noqa: E402


@pytest.fixture
def fresh_run(tmp_path, monkeypatch):
    """A brand new game: day 1, EUR 100.00, nothing in the kitchen.

    Each test gets its own file in a temporary folder, so no test can see
    another one's money and none of them touch the real game.
    """
    db.close()
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "test-game.db")
    logic.start_up()
    yield logic
    db.close()
