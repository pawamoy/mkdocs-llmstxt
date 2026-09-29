# SPDX-License-Identifier: ISC
#
# ISC License
#
# Copyright (c) 2025, Timothée Mazzucotelli and contributors
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

# Configuration options for the MkDocs LLMsTxt plugin.

from __future__ import annotations

from mkdocs.config import config_options as mkconf
from mkdocs.config.base import Config as BaseConfig


class _PluginConfig(BaseConfig):
    """Configuration options for the plugin."""

    autoclean = mkconf.Type(bool, default=True)
    preprocess = mkconf.Optional(mkconf.File(exists=True))
    base_url = mkconf.Optional(mkconf.Type(str))
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
