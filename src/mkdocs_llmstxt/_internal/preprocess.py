# HTML pre-processing.

from __future__ import annotations

import html
import sys
from urllib.parse import urljoin
from importlib.util import module_from_spec, spec_from_file_location
from typing import TYPE_CHECKING

from bs4 import BeautifulSoup as Soup
from bs4.element import NavigableString
from mkdocs.exceptions import PluginError

if TYPE_CHECKING:
    from types import ModuleType

    from bs4 import Tag


def _load_module(module_path: str) -> ModuleType:
    module_name = module_path.rsplit("/", 1)[-1].rsplit(".", 1)[-1]
    module_name = f"mkdocs_llmstxt.user_config.{module_name}"
    spec = spec_from_file_location(module_name, module_path)
    if spec and spec.loader:
        module = module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module
    raise RuntimeError("Spec or loader is null")


def _preprocess(soup: Soup, module_path: str, output: str) -> None:
    """Pre-process HTML with user-defined functions.

    Parameters:
        soup: The HTML (soup) to process before conversion to Markdown.
        module_path: The path of a Python module containing a `preprocess` function.
            The function must accept one and only one argument called `soup`.
            The `soup` argument is an instance of [`bs4.BeautifulSoup`][].
        output: The output path of the relevant Markdown file.

    Returns:
        The processed HTML.
    """
    try:
        module = _load_module(module_path)
    except Exception as error:
        raise PluginError(f"Could not load module: {error}") from error
    try:
        module.preprocess(soup, output)
    except Exception as error:
        raise PluginError(f"Could not pre-process HTML: {error}") from error


def _to_remove(tag: Tag) -> bool:
    # Remove images and SVGs.
    if tag.name in {"img", "svg"}:
        return True
    # Remove links containing images or SVGs.
    if tag.name == "a" and tag.img and _to_remove(tag.img):
        return True

    classes = tag.get("class") or ()

    # Remove permalinks.
    if tag.name == "a" and "headerlink" in classes:
        return True
    # Remove Twemojis.
    if "twemoji" in classes:
        return True
    # Remove tab labels.
    if "tabbed-labels" in classes:  # noqa: SIM103
        return True

    return False


def autoclean(soup: Soup) -> None:
    """Auto-clean the soup by removing elements.

    Parameters:
        soup: The soup to modify.
    """
    # Remove unwanted elements.
    for element in soup.find_all(_to_remove):
        element.decompose()

    # Unwrap autoref elements.
    for element in soup.find_all("autoref"):
        element.replace_with(NavigableString(element.get_text()))

    # Unwrap mkdocstrings div.doc-md-description.
    for element in soup.find_all("div", attrs={"class": "doc-md-description"}):
        element.replace_with(NavigableString(element.get_text().strip()))

    # Remove mkdocstrings labels.
    for element in soup.find_all("span", attrs={"class": "doc-labels"}):
        element.decompose()

    # Remove line numbers from code blocks.
    for element in soup.find_all("table", attrs={"class": "highlighttable"}):
        element.replace_with(Soup(f"<pre>{html.escape(element.find('code').get_text())}</pre>", "html.parser"))  # type: ignore[union-attr]