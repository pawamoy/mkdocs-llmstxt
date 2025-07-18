"""Tests for the plugin."""

from pathlib import Path

import pytest
from bs4 import BeautifulSoup as Soup
from mkdocs.commands.build import build
from mkdocs.config.defaults import MkDocsConfig
from mkdocs_llmstxt._internal.preprocess import transform_source_to_details


@pytest.mark.parametrize(
    "mkdocs_conf",
    [
        {
            "config": {
                "plugins": [
                    {
                        "llmstxt": {
                            "full_output": "llms-full.txt",
                            "sections": {
                                "Index": ["index.md"],
                                "Usage": [{"page1.md": "Some usage docs."}],
                            },
                        },
                    },
                ],
            },
            "pages": {
                "index.md": "# Hello world",
                "page1.md": "# Usage\n\nSome paragraph.",
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


def test_transform_source_to_details():
    """Test that source code tables are transformed to collapsible details."""
    # Sample HTML with a highlighted code table (like mkdocstrings produces)
    html = """
    <div>
        <h3>Some function</h3>
        <table class="highlighttable">
            <tr>
                <td class="linenos"><pre>1\n2\n3</pre></td>
                <td class="code">
                    <pre><code class="language-python">def example_function():
    # This is an example function
    return "Hello, World!"</code></pre>
                </td>
            </tr>
        </table>
    </div>
    """

    soup = Soup(html, "html.parser")
    transform_source_to_details(soup)

    # Check that the table was replaced with details/summary
    assert soup.find("table", class_="highlighttable") is None
    assert soup.find("details") is not None
    assert soup.find("summary") is not None

    # Check that the code content is preserved and wrapped in a code block
    details_content = str(soup.find("details"))
    assert "def example_function():" in details_content
    assert "```python" in details_content
    assert "Source code" in details_content
