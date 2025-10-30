"""Tests for the plugin."""

from pathlib import Path
from textwrap import dedent

import pytest
from mkdocs.commands.build import build
from mkdocs.config.defaults import MkDocsConfig


@pytest.mark.parametrize(
    "mkdocs_conf",
    [
        {
            "config": {
                "plugins": [
                    {
                        "llmstxt": {
                            "full_output": "llms-full.txt",
                            "base_url": "https://example.org/en/0.1.34",
                            "sections": {
                                "Index": ["index.md"],
                                "Usage": [{"page1.md": "Some usage docs."}],
                                "Links": [{"page2.md": "Page with links."}],
                            },
                        },
                    },
                ],
            },
            "pages": {
                "index.md": "# Hello world",
                "dummy.md": "# Hello world",
                "page1.md": "# Usage\n\nSome paragraph.",
                "page2.md": dedent(
                    """
                    # Links

                    [Relative link 1](./index.md)
                    [Relative link 2](./page1.md)
                    [Relative link 3](dummy.md)
                    [Absolute link 1](/abs1/)
                    [Absolute link 2](/abs2/index.md)
                    [External link](https://example.com)
                    [Anchor link](#section)
                    [Email link 1](mailto:test1@example.com)
                    <test2@example.com>
                    [External protocol 1](ftp://example1.com)
                    [External protocol 2](ftp://example2.com/my/)
                    """,
                ),
            },
        },
    ],
    indirect=["mkdocs_conf"],
)
def test_plugin(mkdocs_conf: MkDocsConfig) -> None:
    """Test that page descriptions are correctly handled and included in output."""
    build(config=mkdocs_conf)

    llmstxt = Path(mkdocs_conf.site_dir, "llms.txt")
    assert llmstxt.exists()
    llmstxt_content = llmstxt.read_text()
    assert "Some usage docs." in llmstxt_content
    assert "Some paragraph." not in llmstxt_content

    llmsfulltxt = Path(mkdocs_conf.site_dir, "llms-full.txt")
    assert llmsfulltxt.exists()
    llmsfulltxt_content = llmsfulltxt.read_text()
    assert "Some usage docs." not in llmsfulltxt_content
    assert "Some paragraph." in llmsfulltxt_content

    indexmd = Path(mkdocs_conf.site_dir, "index.md")
    assert indexmd.exists()
    assert "Hello world" in indexmd.read_text()

    page1md = Path(mkdocs_conf.site_dir, "page1/index.md")
    assert page1md.exists()
    assert "Some paragraph." in page1md.read_text()

    page2md = Path(mkdocs_conf.site_dir, "page2/index.md")
    assert page2md.exists()
    page2md_content = page2md.read_text()

    # Check that relative links are made absolute in each page and in the full llmstxt file.
    assert "(https://example.org/en/0.1.34/index.md)" in page2md_content
    assert "(https://example.org/en/0.1.34/page1/index.md)" in page2md_content
    assert "(https://example.org/en/0.1.34/dummy/index.md)" in page2md_content

    assert "(/abs1/)" in page2md_content  # absolute link unchanged
    assert "(/abs2/index.md)" in page2md_content  # absolute link unchanged

    assert "(https://example.com)" in page2md_content  # External link unchanged
    assert "(#section)" in page2md_content  # Anchor link unchanged
    assert "(mailto:test1@example.com)" in page2md_content
    assert "(mailto:test2@example.com)" in page2md_content
    assert "(ftp://example1.com)" in page2md_content
    assert "(ftp://example2.com/my/)" in page2md_content  # index.md not included

    # Check that llmstxt pages (Markdown) contain links to other llmstxt pages, not HTML ones.
    assert '"https://example.org/en/0.1.34/index.html"' not in llmsfulltxt_content
    assert '"https://example.org/en/0.1.34/page1/"' not in llmsfulltxt_content
    assert '"https://example.org/en/0.1.34/page1/index.html"' not in llmsfulltxt_content

    assert '"https://example.org/en/0.1.34/index.html"' not in llmsfulltxt_content
    assert '"https://example.org/en/0.1.34/page1/"' not in llmsfulltxt_content
    assert '"https://example.org/en/0.1.34/page1/index.html"' not in llmsfulltxt_content

    assert '"https://example.org/en/0.1.34/index.html"' not in llmstxt_content
    assert '"https://example.org/en/0.1.34/page1/"' not in llmstxt_content
    assert '"https://example.org/en/0.1.34/page1/index.html"' not in llmstxt_content
