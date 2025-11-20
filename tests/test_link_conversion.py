"""Unit tests for link conversion helpers."""

from __future__ import annotations

import pytest

from mkdocs_llmstxt._internal.plugin import _convert_to_absolute_link

BASE_URI = "https://example.org/en/0.1.34/"
PAGE_DIR = "page2"


@pytest.mark.parametrize(
    ("href", "current_dir", "expected"),
    [
        ("../", PAGE_DIR, "https://example.org/en/0.1.34/index.md"),
        ("../page1/", PAGE_DIR, "https://example.org/en/0.1.34/page1/index.md"),
        ("../dummy/", PAGE_DIR, "https://example.org/en/0.1.34/dummy/index.md"),
        ("section/guide/", "", "https://example.org/en/0.1.34/section/guide/index.md"),
        ("../assets/reference.md", PAGE_DIR, "https://example.org/en/0.1.34/assets/reference.md"),
    ],
)
def test_relative_links_are_made_absolute(href: str, current_dir: str, expected: str) -> None:
    """Relative links should be converted into absolute Markdown URLs."""
    assert _convert_to_absolute_link(href, base_uri=BASE_URI, current_dir=current_dir) == expected


@pytest.mark.parametrize("href", ["/abs1/", "/abs2/index.md"])
def test_absolute_paths_are_untouched(href: str) -> None:
    """Absolute paths must pass through unchanged."""
    assert _convert_to_absolute_link(href, base_uri=BASE_URI, current_dir=PAGE_DIR) == href


@pytest.mark.parametrize(
    "href",
    [
        "https://example.com",
        "ftp://example.com/resource",
        "mailto:test@example.com",
    ],
)
def test_external_links_are_preserved(href: str) -> None:
    """External links should stay untouched."""
    assert _convert_to_absolute_link(href, base_uri=BASE_URI, current_dir=PAGE_DIR) == href


@pytest.mark.parametrize("href", ["#section"])
def test_anchor_links_are_preserved(href: str) -> None:
    """Anchor links are not rewritten."""
    assert _convert_to_absolute_link(href, base_uri=BASE_URI, current_dir=PAGE_DIR) == href
