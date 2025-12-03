

import os
import sys

from loguru import logger
from conf.config import config_manager


def initialize_logger():
    """Initialize and configure the logger."""
    server_cfg = config_manager.server_config

    # remove default Loguru sink (prevents unintended DEBUG console output)
    logger.remove()

    # ensure log directory exists
    os.makedirs("logs", exist_ok=True)

    level = "DEBUG" if getattr(server_cfg, "DEBUG", False) else "INFO"

    # Console sink (colorized)
    logger.add(
        sys.stderr,
        level=level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
        colorize=True,
    )

    # File sink (no ANSI color codes)
    logger.add(
        f"logs/{getattr(server_cfg, 'NAME', 'agiaagentic')}.log",
        rotation="10 MB",
        retention="10 days",
        compression="zip",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
        level=level,
        colorize=False,
    )

    # bind and return the bound logger instance
    bound_logger = logger.bind(app=getattr(server_cfg, "NAME", "agiaagentic"))
    return bound_logger





