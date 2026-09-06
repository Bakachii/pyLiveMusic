"""
Test: Memory Storage
--------------------

Memory storage keeps pyLiveMusic data directly in RAM.

Memory:
    Uses Python dictionaries to store data in memory.

    No additional configuration is required.

    Memory is the default storage backend.

    Data is temporary and will be lost when the server
    stops or restarts.
"""

import asyncio

from pyLiveMusic import Client
from pyLiveMusic.storage import Memory


async def main():
    client = Client(
        HOST="0.0.0.0",          # Optional. Defaults to "0.0.0.0".
        PORT=8000,               # Optional. Defaults to 8000.
        AUTH_KEY="124",          # Optional. Generates a random secret if omitted.
        STORAGE=Memory(),        # Optional. Memory is the default storage.
        player_function=False,   # Optional. Defaults to False.
    )

    try:
        # Start the pyLiveMusic server.
        await client.start()

        # Keep the server running until Ctrl+C or SIGTERM.
        await client.run_until_disconnect()

    finally:
        # Clean up the server and HTTP session.
        await client.stop()


if __name__ == "__main__":
    asyncio.run(main())