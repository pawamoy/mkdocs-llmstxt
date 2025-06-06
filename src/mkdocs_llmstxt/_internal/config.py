# Configuration options for the MkDocs LLMsTxt plugin.

from __future__ import annotations

from mkdocs.config import config_options as mkconf
from mkdocs.config.base import Config as BaseConfig


class _PluginConfig(BaseConfig):
    """Configuration options for the plugin."""

    autoclean = mkconf.Type(bool, default=True)
    preprocess = mkconf.Optional(mkconf.File(exists=True))
    markdown_description = mkconf.Optional(mkconf.Type(str))
    full_output = mkconf.Optional(mkconf.Type(str))
    sections = mkconf.DictOfItems(mkconf.ListOfItems(mkconf.Type(str)))
    prefix_url_per_page = mkconf.Type(bool, default=False)
    use_section_separator = mkconf.Optional(mkconf.Type(str))
    use_section_pages_separator = mkconf.Optional(mkconf.Type(str))
    prefix_url_base_url = mkconf.Optional(mkconf.Type(str))
    include_section_content_in_full_output = mkconf.Type(bool, default=True)
