from pyLiveMusic._webrtc.backend import RoomManager

from pyLiveMusic.storage import (
    Memory,
    MongoDB,
    Redis,
    _MemoryStorage, 
    _MongoStorage,
    _RedisStorage,
)

from pyLiveMusic.persistence import (
    MemoryRoomRepository, 
    MemoryUserRepository, 
    MongoRoomRepository,
    MongoUserRepository
)

class AppState:

    
    def __init__(self, storage):
        self.rooms = None
        self.storage = None
        self.users = None
        self.room_repository = None

        if isinstance(storage, Memory):
            self.MemoryState()

        elif isinstance(storage, MongoDB):
            self.MongoDBState(storage)

        elif isinstance(storage, Redis):
            self.RedisState(storage)

        else:
            raise TypeError("Unsupported storage type")

    def MemoryState(self):
        self.rooms = RoomManager()
        self.storage = _MemoryStorage()
        self.users = MemoryUserRepository()
        self.room_repository = MemoryRoomRepository()

    def MongoDBState(self, storage): 
        self.rooms = RoomManager()
        self.storage = _MongoStorage(
            storage.db_url, 
            storage.db_name,
            storage.user_collection, 
            storage.room_collection
        )
        self.users = MongoUserRepository(storage.user_collection)
        self.room_repository = MongoRoomRepository(storage.room_collection)

    def RedisState(self, storage):
        self.rooms = None
        self.storage = None
        self.users = None
        self.room_repository = None