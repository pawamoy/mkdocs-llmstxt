"""Tests for the plugin."""

import pytest
from duty.tools import mkdocs
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.structure.files import Files
from mkdocs.structure.pages import Page
from types import SimpleNamespace

from mkdocs_llmstxt._internal.plugin import MkdocsLLMsTxtPlugin


def test_plugin() -> None:
    """Run the plugin."""
    with pytest.raises(expected_exception=SystemExit) as exc:
        mkdocs.build()()
    assert exc.value.code == 0


def test_page_descriptions() -> None:
    """Test that page descriptions are correctly handled and included in output."""
    # Create a mock config
    config = MkDocsConfig()
    config.site_name = "Test Project"
    config.site_description = "Test Description"
    config.site_url = "https://test.com/"
    
    # Create plugin instance with test configuration
    plugin = MkdocsLLMsTxtPlugin()
    plugin.load_config({
        "sections": {
            "Test Section": {
                "page1.md": "Description of page 1",
                "page2.md": "Description of page 2"
            }
        }
    })
    
    # Initialize plugin
    plugin.on_config(config)
    
    # Create mock file and page
    file = SimpleNamespace(
        src_uri="page1.md",
        dest_uri="page1.html",
        abs_dest_path="/tmp/page1.html",
        url="page1.html"
    )
    page = Page(
        title="Test Page",
        file=file,
        config=config
    )
    
    # Process page content
    plugin.on_page_content("<html><body>Test content</body></html>", page=page)
    
    # Check that the page info was stored correctly
    assert len(plugin.md_pages["Test Section"]) == 1
    page_info = plugin.md_pages["Test Section"][0]
    assert page_info.title == "Test Page"
    assert page_info.description == "Description of page 1"


def test_mixed_descriptions() -> None:
    """Test that mixing files with and without descriptions works correctly."""
    # Create a mock config
    config = MkDocsConfig()
    config.site_name = "Test Project"
    config.site_url = "https://test.com/"
    
    # Create plugin instance with test configuration
    plugin = MkdocsLLMsTxtPlugin()
    plugin.load_config({
        "sections": {
            "Test Section": {
                "page1.md": "Description of page 1",
                "page2.md": None,
                "page3.md": "Description of page 3"
            }
        }
    })
    
    # Initialize plugin
    plugin.on_config(config)
    
    # Create and process mock pages
    for page_num in range(1, 4):
        file = SimpleNamespace(
            src_uri=f"page{page_num}.md",
            dest_uri=f"page{page_num}.html",
            abs_dest_path=f"/tmp/page{page_num}.html",
            url=f"page{page_num}.html"
        )
        page = Page(
            title=f"Test Page {page_num}",
            file=file,
            config=config
        )
        plugin.on_page_content("<html><body>Test content</body></html>", page=page)
    
    # Check that all pages were processed
    assert len(plugin.md_pages["Test Section"]) == 3
    
    # Verify descriptions
    descriptions = [info.description for info in plugin.md_pages["Test Section"]]
    assert descriptions == ["Description of page 1", None, "Description of page 3"]

def test_no_descriptions() -> None:
    """Test that no descriptions are included when no descriptions are provided."""
    # Create a mock config
    config = MkDocsConfig()
    config.site_name = "Test Project"
    config.site_url = "https://test.com/"

    # Create plugin instance with test configuration
    plugin = MkdocsLLMsTxtPlugin()
    plugin.load_config({
        "sections": {
            "Test Section": [
                "page1.md",
                "page2.md"
            ]
        }
    })

    # Initialize plugin
    plugin.on_config(config)

    # Create and process mock pages
    for page_num in range(1, 3):
        file = SimpleNamespace(
            src_uri=f"page{page_num}.md",
            dest_uri=f"page{page_num}.html",
            abs_dest_path=f"/tmp/page{page_num}.html",
            url=f"page{page_num}.html"
        )
        page = Page(
            title=f"Test Page {page_num}",
            file=file,
            config=config
        )
        plugin.on_page_content("<html><body>Test content</body></html>", page=page)
    
    # Check that all pages were processed
    assert len(plugin.md_pages["Test Section"]) == 2

    descriptions = [info.description for info in plugin.md_pages["Test Section"]]
    assert descriptions == [None, None]
