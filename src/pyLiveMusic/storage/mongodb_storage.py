from pymongo import AsyncMongoClient

class MongoDB:
    def __init__(self, db_url):
        self.db_url = db_url

class _MongoStorage:
    def __init__(self, DB_URL: str):

        self.client = AsyncMongoClient(DB_URL)
        self.storage = self.client["MongoStorage"]

        self.users = self.storage["users"]
        self.rooms = self.storage["rooms"]

    async def connect(self):
        await self.client.admin.command("ping")
        print("MongoDB connected")

    async def close(self):
        await self.client.close()
        print("MongoDB disconnected")