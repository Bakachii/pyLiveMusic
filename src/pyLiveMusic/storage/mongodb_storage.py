from pymongo import AsyncMongoClient

class MongoDB:
    def __init__(
        self, 
        db_url: str | None = None, 
        db_name: str | None = None,
        user_collection: str | None = None, 
        room_collection: str | None = None,
        ):

        self.db_url = db_url
        self.db_name = db_name or "MongoStorage"
        self.user_collection = user_collection or 'users'
        self.room_collection = room_collection or 'rooms'


class _MongoStorage:
    def __init__(
        self, 
        db_url: str, 
        db_name: str,
        user_collection: str, 
        room_collection: str
        ): 

        self.client = AsyncMongoClient(db_url)
        self.storage = self.client[db_name]

        self.users = self.storage[room_collection]
        self.rooms = self.storage[user_collection]

    async def connect(self):
        await self.client.admin.command("ping")
        print("MongoDB connected")

    async def close(self):
        await self.client.close()
        print("MongoDB disconnected")