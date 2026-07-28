import sys
import os
from loguru import logger

LOG_DIR = "./logs"
os.makedirs(LOG_DIR, exist_ok=True)

logger.remove()

# Console logger
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="DEBUG"
)

# File logger
logger.add(
    os.path.join(LOG_DIR, "app.log"),
    rotation="10 MB",
    retention="30 days",
    compression="zip",
    enqueue=True,
    level="INFO"
)

# Error log file
logger.add(
    os.path.join(LOG_DIR, "errors.log"),
    rotation="10 MB",
    retention="60 days",
    level="ERROR"
)

__all__ = ["logger"]
