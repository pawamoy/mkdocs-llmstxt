# SPDX-License-Identifier: ISC
#
# ISC License
#
# Copyright (c) 2025, Timothée Mazzucotelli and contributors
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

"""Configuration for the pytest test suite."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from mkdocs.config.defaults import MkDocsConfig

if TYPE_CHECKING:
    from mkdocs_llmstxt._internal.plugin import MkdocsLLMsTxtPlugin


@pytest.fixture(name="mkdocs_conf")
def fixture_mkdocs_conf(request: pytest.FixtureRequest, tmp_path: Path) -> MkDocsConfig:
    """Yield a MkDocs configuration object."""
    while hasattr(request, "_parent_request") and hasattr(request._parent_request, "_parent_request"):
        request = request._parent_request
    params = getattr(request, "param", {})
    config = params.get("config", {})
    pages = params.get("pages", {})
    conf = MkDocsConfig()
    conf.load_dict(
        {
            "site_name": "Test Project",
            "site_url": "https://example.org/",
            "site_dir": str(tmp_path / "site"),
            "docs_dir": str(tmp_path / "docs"),
            **config,
        },
    )
    Path(conf.docs_dir).mkdir(exist_ok=True)
    for page, content in pages.items():
        page_file = Path(conf.docs_dir, page)
        page_file.parent.mkdir(exist_ok=True)
        page_file.write_text(content)
    assert conf.validate() == ([], [])
    if "toc" not in conf.markdown_extensions:
        # Guaranteed to be added by MkDocs.
        conf.markdown_extensions.insert(0, "toc")
    return conf


@pytest.fixture(name="plugin")
def fixture_plugin(mkdocs_conf: MkDocsConfig) -> MkdocsLLMsTxtPlugin:
    """Return a plugin instance."""
    return mkdocs_conf.plugins["llmstxt"]  # type: ignore[return-value]
