"""Logging Configuration"""

import logging
import sys

def setup_logger(name='arbitrage_engine', level=logging.INFO):
    """Setup logger with consistent formatting"""
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)

    # Format
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    return logger
