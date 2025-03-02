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
