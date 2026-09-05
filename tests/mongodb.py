import asyncio

from pyLiveMusic import Client
from pyLiveMusic.storage import MongoDB


db_url = "mongodb+srv://<username>:<password>@<cluster>.mongodb.net/?retryWrites=true&w=majority"

db_name = "MongoStorage"
user_collection = "users"
room_collection = "rooms"

async def main():
    server = Client(
        HOST="0.0.0.0", # Optional server host. Defaults to "0.0.0.0".
        PORT=5000, # Optional server port. Defaults to 8000.
        AUTH_KEY="124", # Optional string authentication key. Generates a random secret if not provided.

        STORAGE=MongoDB(
            db_url=db_url,
            db_name=db_name,
            user_collection=user_collection,
            room_collection=room_collection,
        ),
    )

    try:
        await server.start() # Start the server after configuring credentials
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass 


"""
MongoDB storage configuration.

db_url:
    The MongoDB connection URL. This is required when using MongoDB storage.

db_name:
    The MongoDB database name.
    Optional. Defaults to "MongoStorage".

user_collection:
    The collection used to store users.
    Optional. Defaults to "users".

room_collection:
    The collection used to store rooms.
    Optional. Defaults to "rooms".

Only db_url is required. The db_name, user_collection,
and room_collection parameters are optional.
"""
