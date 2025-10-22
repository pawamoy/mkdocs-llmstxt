"""Tests for the plugin."""

from pathlib import Path

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
                "page1.md": "# Usage\n\nSome paragraph.",
                "page2.md": "# Links\n\n[Relative link](../index.md)\n[Absolute link](/page1.md)\n[External link](https://example.com)\n[Anchor link](#section)",
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

    # Test relative link conversion
    page2md = Path(mkdocs_conf.site_dir, "page2/index.md")
    assert page2md.exists()
    page2md_content = page2md.read_text()
    
    # Check that relative links are converted to absolute URLs
    assert "https://example.org/en/0.1.34/index.md" in page2md_content  # ../index.md converted
    assert "https://example.org/page1.md" in page2md_content  # /page1.md converted (absolute from domain root)
    assert "https://example.com" in page2md_content  # External link unchanged
    assert "#section" in page2md_content  # Anchor link unchanged
