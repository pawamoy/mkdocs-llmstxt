"""Tests for the plugin."""

import pytest
from duty.tools import mkdocs


def test_plugin() -> None:
    """Run the plugin."""
    with pytest.raises(expected_exception=SystemExit) as exc:
        mkdocs.build()()
    assert exc.value.code == 0
