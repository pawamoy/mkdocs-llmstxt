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

# Logging functions.

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import MutableMapping


class _PluginLogger(logging.LoggerAdapter):
    """A logger adapter to prefix messages with the originating package name."""

    def __init__(self, prefix: str, logger: logging.Logger):
        """Initialize the object.

        Arguments:
            prefix: The string to insert in front of every message.
            logger: The logger instance.
        """
        super().__init__(logger, {})
        self.prefix = prefix

    def process(self, msg: str, kwargs: MutableMapping[str, Any]) -> tuple[str, Any]:
        """Process the message.

        Arguments:
            msg: The message:
            kwargs: Remaining arguments.

        Returns:
            The processed message.
        """
        return f"{self.prefix}: {msg}", kwargs


def _get_logger(name: str) -> _PluginLogger:
    """Return a logger for plugins.

    Arguments:
        name: The name to use with `logging.getLogger`.

    Returns:
        A logger configured to work well in MkDocs,
            prefixing each message with the plugin package name.
    """
    logger = logging.getLogger(f"mkdocs.plugins.{name}")
    return _PluginLogger(name.split(".", 1)[0], logger)
