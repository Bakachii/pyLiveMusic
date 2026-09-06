"""
Test: Client Lifecycle
----------------------

This test demonstrates the basic pyLiveMusic client lifecycle.

Client configuration:

HOST:
    Optional. The host address where the server will listen.
    Defaults to "0.0.0.0".

PORT:
    Optional. The port where the server will listen.
    Defaults to 8000.

AUTH_KEY:
    Optional string used to authenticate requests.
    If not provided, a random secret key will be generated.

STORAGE:
    Optional. Defines the storage backend used by the server.
    Available options are Memory, MongoDB, and Redis.
    Defaults to Memory if not specified.

player_function:
    Optional. Enables the Python player functions such as
    Room and Playback.

    Defaults to False.

    When False:
        The HTTP API is still available and can be used
        through cURL or other HTTP clients.

    When True:
        pyLiveMusic initializes the player classes, which
        can then be accessed using:

            client.get(Room)
            client.get(Playback)

If no configuration is provided, pyLiveMusic will use:

    HOST            -> 0.0.0.0
    PORT            -> 8000
    AUTH_KEY        -> Randomly generated secret
    STORAGE         -> Memory
    player_function -> False


Lifecycle:

    Client()
        ↓
    await client.start()
        ↓
    Server is running
        ↓
    await client.run_until_disconnect()
        ↓
    Ctrl+C / SIGTERM
        ↓
    client.stop()
"""

import asyncio

from pyLiveMusic import Client


async def main():
    client = Client()

    try:
        # Start the server.
        await client.start()

        # Keep the application running until it receives
        # SIGINT (Ctrl+C) or SIGTERM.
        await client.run_until_disconnect()

    finally:
        # Always clean up the server and HTTP client.
        await client.stop()


if __name__ == "__main__":
    asyncio.run(main())