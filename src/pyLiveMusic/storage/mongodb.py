class MongoDB:
    def __init__(
        self, 
        db_url: str | None = None, 
        db_name: str | None = None,
        user_collection: str | None = None, 
        room_collection: str | None = None,
    ):

        try:
            from pymongo import AsyncMongoClient
        except ImportError as exc:
            raise ImportError(
                "To use the MongoDB, you must install pyLiveMusic via "
                "pip install 'pyLiveMusic[mongo]'"
            ) from exc

        self.db_url = db_url
        self.db_name = db_name or "MongoStorage"
        self.user_collection = user_collection or 'users'
        self.room_collection = room_collection or 'rooms'