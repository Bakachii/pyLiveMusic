"""
Test: End Room
--------------

This example shows how to:

1. Enable the player functions.
2. Start pyLiveMusic.
3. Get the initialized Room instance.
4. Create a room.
5. End the room using Room.end().

The Room object is initialized when the client starts
because player_function=True.

We get the initialized Room object using:

    room = client.get(Room)

Creating or ending a room only happens when we
explicitly call the corresponding method.
"""

import asyncio

from pyLiveMusic import Client
from pyLiveMusic.player import Room


async def main():

    # Enable the Python player functions.
    client = Client(player_function=True)

    try:
        # Start the pyLiveMusic server.
        #
        # Because player_function=True, the supported
        # player classes are initialized here.
        await client.start()

        # Get the already-initialized Room instance.
        room = client.get(Room)
 
        # Create a room.
        room_data = await room.create(
            name="Lo-fi",
            room_id="lofi",
        )

        print("CREATED ROOM:")
        print(room_data)

        # End the room.
        ended = await room.end("lofi")

        print("\nENDED ROOM:")
        print(ended)

        # Keep the server running until it is stopped.
        await client.run_until_disconnect()

    finally:
        # Clean up the client.
        await client.stop()


if __name__ == "__main__":
    asyncio.run(main())