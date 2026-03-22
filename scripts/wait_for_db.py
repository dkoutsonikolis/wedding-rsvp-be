import asyncio
import logging
import os
import sys

import asyncpg

DATABASE_URL = os.environ["DATABASE_URL"].replace("+asyncpg", "")
TIMEOUT = int(os.environ.get("DB_WAIT_TIMEOUT", 30))

logging.basicConfig(level=logging.INFO, format="%(message)s", stream=sys.stdout)
logger = logging.getLogger(__name__)


async def wait_for_db():
    for _ in range(TIMEOUT):
        try:
            conn = await asyncpg.connect(DATABASE_URL)
            await conn.close()
            logger.info("Database is up!")
            return
        except Exception:
            logger.info("Waiting for database...")
            await asyncio.sleep(1)
    raise TimeoutError("Database did not become available in time")


if __name__ == "__main__":
    asyncio.run(wait_for_db())
