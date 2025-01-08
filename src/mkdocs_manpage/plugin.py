"""MkDocs plugin that generates a manpage at the end of the build."""

from __future__ import annotations

import fnmatch
import subprocess
import tempfile
from collections import defaultdict
from datetime import date
from importlib import metadata
from pathlib import Path
from shutil import which
from typing import TYPE_CHECKING

from mkdocs.config.defaults import MkDocsConfig
from mkdocs.exceptions import PluginError
from mkdocs.plugins import BasePlugin

from mkdocs_manpage.config import PluginConfig
from mkdocs_manpage.logger import get_logger
from mkdocs_manpage.preprocess import preprocess

if TYPE_CHECKING:
    from typing import Any

    from mkdocs.config.defaults import MkDocsConfig
    from mkdocs.structure.files import Files
    from mkdocs.structure.pages import Page


logger = get_logger(__name__)


def _log_pandoc_output(output: str) -> None:
    for line in output.split("\n"):
        if line.strip():
            logger.debug(f"pandoc: {line.strip()}")


section_headers = {
    "1": "User Commands",
    "2": "System Calls Manual",
    "3": "Library Functions Manual",
    "4": "Kernel Interfaces Manual",
    "5": "File Formats Manual",
    "6": "Games Manual",
    "7": "Miscellaneous Information Manual",
    "8": "System Administration",
    "9": "Kernel Routines",
}


class MkdocsManpagePlugin(BasePlugin[PluginConfig]):
    """The MkDocs plugin to generate manpages.

    This plugin defines the following event hooks:

    - `on_page_content`
    - `on_post_build`

    Check the [Developing Plugins](https://www.mkdocs.org/user-guide/plugins/#developing-plugins) page of `mkdocs`
    for more information about its plugin system.
    """

    mkdocs_config: MkDocsConfig

    def __init__(self) -> None:  # noqa: D107
        self.html_pages: dict[str, dict[str, str]] = defaultdict(dict)

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
        """Expand inputs for manual pages.

        Hook for the [`on_files` event](https://www.mkdocs.org/user-guide/plugins/#on_files).
        In this hook we expand inputs for each manual pages (glob patterns using `*`).

        Parameters:
            files: The collection of MkDocs files.
            config: The MkDocs configuration.

        Returns:
            Modified collection or none.
        """
        for manpage in self.config.pages:
            manpage["inputs"] = self._expand_inputs(manpage["inputs"], page_uris=list(files.src_uris.keys()))
        return files

    def on_page_content(self, html: str, *, page: Page, **kwargs: Any) -> str | None:  # noqa: ARG002
        """Record pages contents.

        Hook for the [`on_page_content` event](https://www.mkdocs.org/user-guide/plugins/#on_page_content).
        In this hook we simply record the HTML of the pages into a dictionary whose keys are the pages' URIs.

        Parameters:
            html: The page HTML.
            page: The page object.
        """
        if not self.config.enabled:
            return None
        for manpage in self.config.pages:
            if page.file.src_uri in manpage["inputs"]:
                logger.debug(f"Adding page {page.file.src_uri} to manpage {manpage['output']}")
                self.html_pages[manpage["output"]][page.file.src_uri] = html
        return html

    def on_post_build(self, config: MkDocsConfig, **kwargs: Any) -> None:  # noqa: ARG002
        """Combine all recorded pages contents and convert it to a manual page with Pandoc.

        Hook for the [`on_post_build` event](https://www.mkdocs.org/user-guide/plugins/#on_post_build).
        In this hook we concatenate all previously recorded HTML, and convert it to a manual page with Pandoc.

        Parameters:
            config: MkDocs configuration.
        """
        if not self.config.enabled:
            return
        pandoc = which("pandoc")
        if pandoc is None:
            logger.debug("Could not find pandoc executable, trying to call 'pandoc' directly")
            pandoc = "pandoc"

        for page in self.config.pages:
            try:
                html = "\n\n".join(self.html_pages[page["output"]][input_page] for input_page in page["inputs"])
            except KeyError as error:
                raise PluginError(str(error)) from error

            if self.config.get("preprocess"):
                html = preprocess(html, self.config["preprocess"], page["output"])

            output_file = Path(config.config_file_path).parent.joinpath(page["output"])
            output_file.parent.mkdir(parents=True, exist_ok=True)
            section = output_file.suffix[1:]
            section_header = page.get("header", section_headers.get(section, section_headers["1"]))
            title = page.get("title", self.mkdocs_config.site_name)

            with tempfile.NamedTemporaryFile("w", prefix="mkdocs_manpage_", suffix=".1.html", encoding="utf8") as temp_file:
                temp_file.write(html)
                pandoc_variables = [
                    f"title:{title}",
                    f"section:{section}",
                    f"date:{date.today().strftime('%Y-%m-%d')}",  # noqa: DTZ011
                    f"footer:mkdocs-manpage v{metadata.version('mkdocs-manpage')}",
                    f"header:{section_header}",
                ]
                pandoc_options = [
                    "--verbose",
                    "--standalone",
                    "--wrap=none",
                ]
                pandoc_command = [
                    pandoc,
                    *pandoc_options,
                    *[f"-V{var}" for var in pandoc_variables],
                    "--to",
                    "man",
                    temp_file.name,
                    "-o",
                    str(output_file),
                ]
                pandoc_process = subprocess.run(  # noqa: S603
                    pandoc_command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    check=False,
                )
            _log_pandoc_output(pandoc_process.stdout)
            logger.info(f"Generated manpage {output_file}")
