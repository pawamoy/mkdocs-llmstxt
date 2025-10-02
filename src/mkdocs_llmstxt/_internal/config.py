# Configuration options for the MkDocs LLMsTxt plugin.

from __future__ import annotations

from mkdocs.config import config_options as mkconf
from mkdocs.config.base import Config as BaseConfig


class _PluginConfig(BaseConfig):
    """Configuration options for the plugin."""

    autoclean = mkconf.Type(bool, default=True)
    preprocess = mkconf.Optional(mkconf.File(exists=True))
    docs_version = mkconf.Optional(mkconf.Type(str))
    markdown_description = mkconf.Optional(mkconf.Type(str))
    full_output = mkconf.Optional(mkconf.Type(str))
    sections = mkconf.DictOfItems(
        # Each list item can either be:
        #
        # - a string representing the source file path (possibly with glob patterns)
        # - a mapping where the single key is the file path and the value is its description.
        #
        # We therefore accept both `str` and `dict` values.
        mkconf.ListOfItems(mkconf.Type((str, dict))),
    )
