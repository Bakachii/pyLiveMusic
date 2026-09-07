import asyncio

from pyLiveMusic import Client
from pyLiveMusic.player import Queue, Room


async def main():

    # Enable the Python player functions.
    client = Client(player_function=True)

    try:
        # Start the pyLiveMusic server.
        await client.start()

        # Get the already-initialized player instances.
        room = client.get(Room)
        queue = client.get(Queue)

        # Create a room so that we have a room to use.
        data = await room.create(name="Lo-fi")

        room_id = data["room_id"]

        # Add the first track.
        first = await queue.add_track(
            room_id=room_id,
            title="Audio Title 1",
            path="/path/to/audio1.mp3",
        )

        # Add the second track.
        second = await queue.add_track(
            room_id=room_id,
            title="Audio Title 2",
            path="/path/to/audio2.mp3",
        )

        print("ADDED TRACK 1:")
        print(first)

        print("\nADDED TRACK 2:")
        print(second)

        # Show the queue before clearing it.
        queue_before = await queue.get_queue(room_id)

        print("\nQUEUE BEFORE CLEAR:")
        print(queue_before)

        # Clear the entire queue.
        cleared = await queue.clear_queue(room_id)

        print("\nCLEARED QUEUE:")
        print(cleared)

        # Keep the server running until it is stopped.
        await client.run_until_disconnect()

    finally:
        # Clean up the client.
        await client.stop()


if __name__ == "__main__":
    asyncio.run(main())