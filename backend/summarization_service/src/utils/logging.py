# src/utils/logging.py

import logging
import sys
from backend.summarization_service.src.config.settings import settings

def setup_logger(name: str = "summiva"):
    logger = logging.getLogger(name)
    logger.setLevel(settings.LOG_LEVEL.upper())

    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
    )
    handler.setFormatter(formatter)

    if not logger.hasHandlers():
        logger.addHandler(handler)

    return logger
