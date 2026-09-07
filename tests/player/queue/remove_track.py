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

        # Add a track so that we have something to remove.
        added = await queue.add_track(
            room_id=room_id,
            title="Audio Title",
            path="/path/to/audio.mp3",
        )

        print("ADDED TRACK:")
        print(added)

        # Remove the track using its ID.
        removed = await queue.remove_track(
            room_id=room_id,
            track_id=added["id"],
        )

        print("\nREMOVED TRACK:")
        print(removed)

        # Keep the server running until it is stopped.
        await client.run_until_disconnect()

    finally:
        # Clean up the client.
        await client.stop()


if __name__ == "__main__":
    asyncio.run(main())