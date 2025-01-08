"""HTML pre-processing."""

from __future__ import annotations

import sys
from importlib.util import module_from_spec, spec_from_file_location
from typing import TYPE_CHECKING

from mkdocs.exceptions import PluginError

if TYPE_CHECKING:
    from types import ModuleType


def _load_module(module_path: str) -> ModuleType:
    module_name = module_path.rsplit("/", 1)[-1].rsplit(".", 1)[-1]
    module_name = f"mkdocs_manpage.user_config.{module_name}"
    spec = spec_from_file_location(module_name, module_path)
    if spec and spec.loader:
        module = module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module
    raise RuntimeError("Spec or loader is null")


def preprocess(html: str, module_path: str, output: str) -> str:
    """Pre-process HTML with user-defined functions.

    Parameters:
        html: The HTML to process before conversion to a manpage.
        module_path: The path of a Python module containing a `preprocess` function.
            The function must accept one and only one argument called `soup`.
            The `soup` argument is an instance of [`bs4.BeautifulSoup`][].
        output: The output path of the relevant manual page.

    Returns:
        The processed HTML.
    """
    try:
        from bs4 import BeautifulSoup
    except ImportError as error:
        raise PluginError(
            "mkdocs-manpage must be installed with the `preprocess` extra to use HTML pre-processing: "
            "`pip install mkdocs-manpage[preprocess]",
        ) from error
    try:
        module = _load_module(module_path)
    except Exception as error:
        raise PluginError(f"Could not load module: {error}") from error
    soup = BeautifulSoup(html, "lxml")
    try:
        module.preprocess(soup, output)
    except Exception as error:
        raise PluginError(f"Could not pre-process HTML: {error}") from error
    return str(soup)
