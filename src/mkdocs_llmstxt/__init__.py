"""mkdocs-llmstxt package.

MkDocs plugin to generate an /llms.txt file.
"""

from __future__ import annotations

from mkdocs_llmstxt._internal.plugin import MkdocsLLMsTxtPlugin
from mkdocs_llmstxt._internal.preprocess import autoclean

__all__: list[str] = [
    "MkdocsLLMsTxtPlugin",
    "autoclean",
]
