import asyncio

from pyLiveMusic import Client
from pyLiveMusic.player import Queue, Room


async def main():

    # Enable the Python player functions.
    client = Client(player_function=True)

    try:
        # Start the pyLiveMusic server.
        #
        # Because player_function=True, the supported
        # player classes are initialized here.
        await client.start()

        # Get the already-initialized player instances.
        room = client.get(Room)
        queue = client.get(Queue)

        # Create a room so that we have a room to use.
        data = await room.create(name="Lo-fi")

        # Add a track so that the queue contains something.
        added = await queue.add_track(
            room_id=data['room_id'],
            title="Audio Title",
            path="/home/bakachii/stuffs/codes/python/pyLiveMusic/audio2.mp3",
        )

        print("ADDED TRACK:")
        print(added)

        # Get the queue using its room ID.
        queue_data = await queue.get_queue(data['room_id'])

        print("\\nQUEUE DATA:")
        print(queue_data)

        # Keep the server running until it is stopped.
        await client.run_until_disconnect()

    finally:
        # Clean up the client.
        await client.stop()


if __name__ == "__main__":
    asyncio.run(main())