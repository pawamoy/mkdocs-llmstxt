# MkDocs plugin that generates a Markdown file at the end of the build.

from __future__ import annotations

import fnmatch
from itertools import chain
from pathlib import Path
from typing import TYPE_CHECKING, NamedTuple, cast
from urllib.parse import urljoin

import mdformat
from bs4 import BeautifulSoup as Soup
from bs4 import Tag
from markdownify import ATX, MarkdownConverter
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.plugins import BasePlugin
from mkdocs.structure.pages import Page

from mkdocs_llmstxt._internal.config import _PluginConfig
from mkdocs_llmstxt._internal.logger import _get_logger
from mkdocs_llmstxt._internal.preprocess import _preprocess, autoclean

if TYPE_CHECKING:
    from typing import Any

    from mkdocs.config.defaults import MkDocsConfig
    from mkdocs.structure.files import Files
    from mkdocs.structure.pages import Page


_logger = _get_logger(__name__)


class _MDPageInfo(NamedTuple):
    title: str
    path_md: Path
    md_url: str
    content: str


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

    _base_url: str
    _sections: dict[str, dict[str, str]]
    _file_uris: set[str]
    _md_pages: dict[str, _MDPageInfo]

    def _expand_inputs(self, inputs: list[str | dict[str, str]], page_uris: list[str]) -> dict[str, str]:
        expanded: dict[str, str] = {}
        for input_item in inputs:
            if isinstance(input_item, dict):
                input_file, description = next(iter(input_item.items()))
            else:
                input_file = input_item
                description = ""
            if "*" in input_file:
                for match in fnmatch.filter(page_uris, input_file):
                    expanded[match] = description
            else:
                expanded[input_file] = description
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
        if config.site_url is None:
            raise ValueError("'site_url' must be set in the MkDocs configuration to be used with the 'llmstxt' plugin")
        self.mkdocs_config = config

        # Use `base_url` if it exists.
        if self.config.base_url is not None:
            self._base_url = cast("str", self.config.base_url)
        else:
            # Use `site_url`, which we assume to be always specified.
            self._base_url = cast("str", self.mkdocs_config.site_url)
        if not self._base_url.endswith("/"):
            self._base_url += "/"

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
        page_uris = list(files.src_uris)
        self._sections = {
            section_name: self._expand_inputs(file_list, page_uris=page_uris)  # type: ignore[arg-type]
            for section_name, file_list in self.config.sections.items()
        }
        self._file_uris = set(chain.from_iterable(self._sections.values()))
        self._md_pages = {}
        return files

    def on_page_content(self, html: str, *, page: Page, **kwargs: Any) -> str | None:  # noqa: ARG002
        """Convert page content into a Markdown file and save the result to be processed in the `on_post_build` hook.

        Hook for the [`on_page_content` event](https://www.mkdocs.org/user-guide/plugins/#on_page_content).

        Parameters:
            html: The rendered HTML.
            page: The page object.
        """
        if (src_uri := page.file.src_uri) in self._file_uris:
            path_md = Path(page.file.abs_dest_path).with_suffix(".md")
            page_md = _generate_page_markdown(
                html,
                should_autoclean=self.config.autoclean,
                preprocess=self.config.preprocess,
                path=str(path_md),
                base_uri=self._base_url,
                page_uri=page.file.dest_uri
            )

            md_url = Path(page.file.dest_uri).with_suffix(".md").as_posix()
            # Apply the same logic as in the `Page.url` property.
            if md_url in (".", "./"):
                md_url = ""
            md_url = urljoin(self._base_url, md_url)

            self._md_pages[src_uri] = _MDPageInfo(
                title=str(page.title) if page.title is not None else src_uri,
                path_md=path_md,
                md_url=md_url,
                content=page_md,
            )

        return html

    def on_post_build(self, *, config: MkDocsConfig, **kwargs: Any) -> None:  # noqa: ARG002
        """Create the final `llms.txt` file and the MD files for all selected pages.

        Hook for the [`on_post_build` event](https://www.mkdocs.org/user-guide/plugins/#on_post_build).

        Parameters:
            config: MkDocs configuration.
        """
        output_file = Path(config.site_dir).joinpath("llms.txt")
        output_file.parent.mkdir(parents=True, exist_ok=True)
        markdown = f"# {config.site_name}\n\n"

        if config.site_description is not None:
            markdown += f"> {config.site_description}\n\n"

        if self.config.markdown_description is not None:
            markdown += f"{self.config.markdown_description}\n\n"

        full_markdown = markdown

        for section_name, page_uris in self._sections.items():
            markdown += f"## {section_name}\n\n"
            for page_uri, desc in page_uris.items():
                if page_uri not in self._md_pages:
                    _logger.warning(f"Page URI '{page_uri}' not found in the generated pages. Skipping.")
                    continue
                page_title, path_md, md_url, content = self._md_pages[page_uri]
                path_md.write_text(content, encoding="utf8")
                _logger.debug(f"Generated MD file to {path_md}")
                markdown += f"- [{page_title}]({md_url}){(': ' + desc) if desc else ''}\n"
            markdown += "\n"

        output_file.write_text(markdown, encoding="utf8")
        _logger.debug("Generated file /llms.txt")

        if self.config.full_output is not None:
            full_output_file = Path(config.site_dir).joinpath(self.config.full_output)
            for section_name, page_uris in self._sections.items():
                list_content = "\n".join(
                    self._md_pages[page_uri].content for page_uri in page_uris if page_uri in self._md_pages
                )
                full_markdown += f"# {section_name}\n\n{list_content}"
            full_output_file.write_text(full_markdown, encoding="utf8")
            _logger.debug(f"Generated file /{self.config.full_output}.txt")


def _language_callback(tag: Tag) -> str:
    for css_class in chain(tag.get("class") or (), (tag.parent.get("class") or ()) if tag.parent else ()):
        if css_class.startswith("language-"):
            return css_class[9:]
    return ""


_converter = MarkdownConverter(
    bullets="-",
    code_language_callback=_language_callback,
    escape_underscores=False,
    heading_style=ATX,
)


def _generate_page_markdown(
    html: str,
    *,
    should_autoclean: bool,
    preprocess: str | None,
    path: str,
    base_uri: str,
    page_uri: str
) -> str:
    """Convert HTML to Markdown.

    Parameters:
        html: The HTML content.
        should_autoclean: Whether to autoclean the HTML.
        preprocess: An optional path of a Python module containing a `preprocess` function.
        path: The output path of the relevant Markdown file.
        base_uri: The base URI of the site.
        page_uri: The destination URI of the page.
    Returns:
        The Markdown content.
    """
    soup = Soup(html, "html.parser")
    if should_autoclean:
        autoclean(soup)
    if preprocess:
        _preprocess(soup, preprocess, path)
    _convert_to_absolute_links(soup, base_uri, page_uri)
    return mdformat.text(
        _converter.convert_soup(soup),
        options={"wrap": "no"},
        extensions=("tables",),
    )


def _convert_to_absolute_links(soup: Soup, base_uri: str, page_uri: str) -> None:
    """Convert relative links to absolute ones in the HTML.

    Parameters:
        soup: The soup to modify.
        base_uri: The base URI of the site.
        page_uri: The destination URI of the page.
    """
    current_dir = Path(page_uri).parent.as_posix()

    # Find all anchor tags with `href` attributes.
    for link in soup.find_all("a", href=True):
        href = link.get("href")

        # Skip if `href` is not a string or is empty.
        if not isinstance(href, str) or not href:
            continue

        # Skip if it's already an absolute URL (starts with `http://` or `https://`).
        if href.startswith(("http://", "https://")):
            continue

        # Skip if it's a `mailto:` or other protocol links.
        if ":" in href and not href.startswith("/"):
            continue

        # Skip if it's an anchor link (starts with `#`).
        if href.startswith("#"):
            continue

        # Convert relative link to absolute.
        if href.startswith("/"):
            # Absolute path from site root.
            final_href = urljoin(base_uri, href)
        else:
            # Relative path from current directory.
            relative_base = urljoin(base_uri, current_dir + "/") if current_dir else base_uri
            final_href = urljoin(relative_base, href)

        # Convert directory paths (ending with `/`) to point to `index.md` files.
        if final_href.endswith("/"):
            final_href = final_href + "index.md"

        link["href"] = final_href
