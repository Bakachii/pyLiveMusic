"""
Test: Room Creation
-------------------

This test demonstrates how to create a room using
the player functions.

To use classes such as Room, enable player functions:

    player_function=True

When the client starts, pyLiveMusic initializes the
supported player classes.

We can then get the Room instance using:

    room = client.get(Room)

The Room object does not create a room by itself.

We still have to call:

    await room.create(...)

to actually create the room.
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
        # Because player_function=True, the Room
        # and other supported player classes are
        # initialized here.
        await client.start()

        # Get the already-initialized Room instance.
        room = client.get(Room)

        # Create a room.
        #
        # name:
        #     Optional. Defaults to "Private Room".
        #
        # room_id:
        #     Optional. Use this when you want your
        #     own unique room ID.
        data = await room.create( 
            name="Lo-fi",
            room_id="hello",
        )

        print("ROOM DATA:")
        print(data)

        # Keep the server running until it is stopped.
        await client.run_until_disconnect()

    finally:
        # Clean up the server and HTTP session.
        await client.stop()


if __name__ == "__main__":
    asyncio.run(main())