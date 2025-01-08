"""Configuration options for the MkDocs Manpage plugin."""

from __future__ import annotations

from mkdocs.config import config_options as mkconf
from mkdocs.config.base import Config as BaseConfig


class PageConfig(BaseConfig):
    """Sub-config for each manual page."""

    title = mkconf.Type(str)
    header = mkconf.Type(str)
    output = mkconf.File(exists=False)
    inputs = mkconf.ListOfItems(mkconf.Type(str))


class PluginConfig(BaseConfig):
    """Configuration options for the plugin."""

    enabled = mkconf.Type(bool, default=True)
    preprocess = mkconf.File(exists=True)
    pages = mkconf.ListOfItems(mkconf.SubConfig(PageConfig))
