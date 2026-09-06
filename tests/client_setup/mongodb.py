"""
MongoDB storage configuration.

db_url:
    The MongoDB connection URL.
    Required when using MongoDB storage.

db_name:
    The MongoDB database name.
    Optional. Defaults to "MongoStorage".

user_collection:
    The collection used to store users.
    Optional. Defaults to "users".

room_collection:
    The collection used to store rooms.
    Optional. Defaults to "rooms".

Only db_url is required.
The remaining parameters are optional.
"""

import asyncio

from pyLiveMusic import Client
from pyLiveMusic.storage import MongoDB


db_url = (
    "mongodb+srv://<username>:<password>"
    "@<cluster>.mongodb.net/?retryWrites=true&w=majority"
)

db_name = "MongoStorage"
user_collection = "users"
room_collection = "rooms"


async def main():
    client = Client(
        HOST="0.0.0.0",       # Optional. Defaults to "0.0.0.0".
        PORT=8000,            # Optional. Defaults to 8000.
        AUTH_KEY="124",       # Optional. Generates a random secret if omitted.

        STORAGE=MongoDB(
            db_url=db_url,
            db_name=db_name,
            user_collection=user_collection,
            room_collection=room_collection,
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