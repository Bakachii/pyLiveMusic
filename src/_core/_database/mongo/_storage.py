class _MongoStorage:
    from pymongo import AsyncMongoClient
    
    def __init__(
        self,
        db_url: str,
        db_name: str,
        user_collection: str,
        room_collection: str,
    ):
        try:
            from pymongo import AsyncMongoClient
        except ImportError as exc:
            raise ImportError(
                "To use the MongoDB, you must install pyLiveMusic via "
                "pip install 'pyLiveMusic[mongo]'"
            ) from exc
        self.client = AsyncMongoClient(db_url)
        self.storage = self.client[db_name]

        self.users = self.storage[user_collection]
        self.rooms = self.storage[room_collection]

        
    async def connect(self):
        await self.client.admin.command("ping")
        print("MongoDB connected")

    async def close(self):
        await self.client.close()
        print("MongoDB disconnected")