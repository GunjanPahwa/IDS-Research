"""Structured logging initialization for NIDS FastAPI application."""

import logging
import sys
from app.config import settings


def setup_logging() -> None:
    """Configure system logger format and level."""
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    log_format = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"

    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[logging.StreamHandler(sys.stdout)],
        force=True,
    )


logger = logging.getLogger("nids_api")
