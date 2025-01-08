"""Tests for the plugin."""

import os

import pytest
from duty.tools import mkdocs


def test_plugin() -> None:
    """Run the plugin."""
    os.environ["MANPAGE"] = "true"
    with pytest.raises(expected_exception=SystemExit) as exc:
        mkdocs.build()()
    assert exc.value.code == 0
