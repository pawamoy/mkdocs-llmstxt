# MkDocs plugin that generates a Markdown file at the end of the build.

from __future__ import annotations

import fnmatch
from collections import defaultdict
from itertools import chain
from pathlib import Path
from typing import TYPE_CHECKING

import mdformat
from bs4 import BeautifulSoup as Soup
from bs4 import Tag
from markdownify import ATX, MarkdownConverter
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.exceptions import PluginError
from mkdocs.plugins import BasePlugin

from mkdocs_llmstxt._internal.config import _PluginConfig
from mkdocs_llmstxt._internal.logger import _get_logger
from mkdocs_llmstxt._internal.preprocess import autoclean, _preprocess

if TYPE_CHECKING:
    from typing import Any

    from mkdocs.config.defaults import MkDocsConfig
    from mkdocs.structure.files import Files
    from mkdocs.structure.pages import Page


_logger = _get_logger(__name__)


class MkdocsLLMsTxtPlugin(BasePlugin[_PluginConfig]):
    """The MkDocs plugin to generate an `llms.txt` file.

    This plugin defines the following event hooks:

    - `on_page_content`
    - `on_post_build`

    Check the [Developing Plugins](https://www.mkdocs.org/user-guide/plugins/#developing-plugins) page of `mkdocs`
    for more information about its plugin system.
    """

    mkdocs_config: MkDocsConfig
    """The global MkDocs configuration."""

    def __init__(self) -> None:
        self.html_pages: dict[str, dict[str, str]] = defaultdict(dict)
        """Dictionary to store the HTML contents of pages."""

    def _expand_inputs(self, inputs: list[str], page_uris: list[str]) -> list[str]:
        expanded: list[str] = []
        for input_file in inputs:
            if "*" in input_file:
                expanded.extend(fnmatch.filter(page_uris, input_file))
            else:
                expanded.append(input_file)
        return expanded

    def on_config(self, config: MkDocsConfig) -> MkDocsConfig | None:
        """Save the global MkDocs configuration.

        Hook for the [`on_config` event](https://www.mkdocs.org/user-guide/plugins/#on_config).
        In this hook, we save the global MkDocs configuration into an instance variable,
        to re-use it later.

        Arguments:
            config: The MkDocs config object.

        Returns:
            The same, untouched config.
        """
        self.mkdocs_config = config
        return config

    def on_files(self, files: Files, *, config: MkDocsConfig) -> Files | None:  # noqa: ARG002
        """Expand inputs for generated files.

        Hook for the [`on_files` event](https://www.mkdocs.org/user-guide/plugins/#on_files).
        In this hook we expand inputs for generated file (glob patterns using `*`).

        Parameters:
            files: The collection of MkDocs files.
            config: The MkDocs configuration.

        Returns:
            Modified collection or none.
        """
        for file in self.config.files:
            file["inputs"] = self._expand_inputs(file["inputs"], page_uris=list(files.src_uris.keys()))
        return files

    def on_page_content(self, html: str, *, page: Page, **kwargs: Any) -> str | None:  # noqa: ARG002
        """Record pages contents.

        Hook for the [`on_page_content` event](https://www.mkdocs.org/user-guide/plugins/#on_page_content).
        In this hook we simply record the HTML of the pages into a dictionary whose keys are the pages' URIs.

        Parameters:
            html: The rendered HTML.
            page: The page object.
        """
        for file in self.config.files:
            if page.file.src_uri in file["inputs"]:
                _logger.debug(f"Adding page {page.file.src_uri} to page {file['output']}")
                self.html_pages[file["output"]][page.file.src_uri] = html
        return html

    def on_post_build(self, config: MkDocsConfig, **kwargs: Any) -> None:  # noqa: ARG002
        """Combine all recorded pages contents and convert it to a Markdown file with BeautifulSoup and Markdownify.

        Hook for the [`on_post_build` event](https://www.mkdocs.org/user-guide/plugins/#on_post_build).
        In this hook we concatenate all previously recorded HTML, and convert it to Markdown using Markdownify.

        Parameters:
            config: MkDocs configuration.
        """

        def language_callback(tag: Tag) -> str:
            for css_class in chain(tag.get("class") or (), (tag.parent.get("class") or ()) if tag.parent else ()):
                if css_class.startswith("language-"):
                    return css_class[9:]
            return ""

        converter = MarkdownConverter(
            bullets="-",
            code_language_callback=language_callback,
            escape_underscores=False,
            heading_style=ATX,
        )

        for file in self.config.files:
            try:
                html = "\n\n".join(self.html_pages[file["output"]][input_page] for input_page in file["inputs"])
            except KeyError as error:
                raise PluginError(str(error)) from error

            soup = Soup(html, "html.parser")
            if self.config.autoclean:
                autoclean(soup)
            if self.config.preprocess:
                _preprocess(soup, self.config.preprocess, file["output"])

            output_file = Path(config.site_dir).joinpath(file["output"])
            output_file.parent.mkdir(parents=True, exist_ok=True)
            markdown = mdformat.text(converter.convert_soup(soup), options={"wrap": "no"})
            output_file.write_text(markdown, encoding="utf8")

            _logger.info(f"Generated file /{file['output']}")
