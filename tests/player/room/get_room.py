"""
Test: Get Room
--------------

This example shows how to:

1. Enable the player functions.
2. Start pyLiveMusic.
3. Get the initialized Room instance.
4. Create a room.
5. Retrieve the room using Room.get().

The Room object is initialized when the client starts
because player_function=True.

We get the initialized Room object using:

    room = client.get(Room)

The room is only created when we explicitly call:

    await room.create(...)

And it is retrieved when we explicitly call:

    await room.get(...)
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

        # Create a room so that we have a room to retrieve.
        created_room = await room.create(
            name="Lo-fi",
            room_id="hello",
        )

        print("CREATED ROOM:")
        print(created_room)

        # Get the room using its room ID.
        room_data = await room.get("hello")

        print("\nROOM DATA:")
        print(room_data)

        # Keep the server running until it is stopped.
        await client.run_until_disconnect()

    finally:
        # Clean up the client.
        await client.stop()


if __name__ == "__main__":
    asyncio.run(main())