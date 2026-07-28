import asyncio
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.core.database import init_db
from config.logger import logger


async def main():
    logger.info("Initializing Enterprise AI Database Schema...")
    await init_db()
    logger.info("Database schema initialized successfully.")

if __name__ == "__main__":
    asyncio.run(main())
