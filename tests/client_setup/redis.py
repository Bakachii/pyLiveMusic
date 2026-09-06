"""
Redis storage configuration.

db_url:
    The Redis connection URL.
    Required when using Redis storage.

    Example:
        redis://localhost:6379

db:
    The Redis database number to use.
    Optional. Defaults to 0.

    Example:
        Redis(db_url=DB_URL, db=1)

key_prefix:
    A prefix added to pyLiveMusic Redis keys.
    Optional. Defaults to "pylivemusic".

    Example:
        Redis(
            db_url=DB_URL,
            key_prefix="my_music_app",
        )

Only db_url is required.
The db and key_prefix parameters are optional.
"""

import asyncio

from pyLiveMusic import Client
from pyLiveMusic.storage import Redis


db_url = "redis://localhost:6379"
db = 0
key_prefix = "pylivemusic"


async def main():
    client = Client(
        HOST="0.0.0.0",       # Optional. Defaults to "0.0.0.0".
        PORT=8000,            # Optional. Defaults to 8000.
        AUTH_KEY="124",       # Optional. Generates a random secret if omitted.

        STORAGE=Redis(
            db_url=db_url,
            db=db,
            key_prefix=key_prefix,
        ),

        player_function=False,   # Optional. Defaults to False.
    )

    try:
        await client.start()
        await client.run_until_disconnect()
    finally:
        await client.stop()


if __name__ == "__main__":
    asyncio.run(main())