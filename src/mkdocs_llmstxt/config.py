"""Configuration options for the MkDocs LLMsTxt plugin."""

from __future__ import annotations

from mkdocs.config import config_options as mkconf
from mkdocs.config.base import Config as BaseConfig


class FileConfig(BaseConfig):
    """Sub-config for each Markdown file."""

    output = mkconf.Type(str)
    inputs = mkconf.ListOfItems(mkconf.Type(str))


class PluginConfig(BaseConfig):
    """Configuration options for the plugin."""

    autoclean = mkconf.Type(bool, default=True)
    preprocess = mkconf.Optional(mkconf.File(exists=True))
    files = mkconf.ListOfItems(mkconf.SubConfig(FileConfig))
