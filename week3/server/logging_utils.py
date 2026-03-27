"""Logging helpers for the Week 3 MCP server."""

from __future__ import annotations

import logging
import sys


LOGGER_NAME = "week3.openmeteo_mcp"


def configure_logging() -> logging.Logger:
    """Configure stderr-only logging for an STDIO MCP server."""
    logger = logging.getLogger(LOGGER_NAME)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
        logger.addHandler(handler)

    logger.setLevel(logging.INFO)
    logger.propagate = False

    for noisy_logger_name in ("httpx", "httpcore"):
        logging.getLogger(noisy_logger_name).setLevel(logging.WARNING)

    return logger
