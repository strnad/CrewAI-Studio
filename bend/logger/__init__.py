"""
범용 Logger 패키지

사용법:
    from logger import get_logger
    logger = get_logger()
    logger.info("메시지", key1="value1", key2="value2")
"""

from .logger import get_logger, configure, Logger
from .log_config import LEVEL_COLORS

__all__ = [
    "get_logger",
    "configure", 
    "Logger",
    "LEVEL_COLORS",
]

__version__ = "1.0.0"