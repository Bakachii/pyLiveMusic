from pyLiveMusic._webrtc.backend import RoomManager

from pyLiveMusic.storage import (
    _MemoryStorage, 
    _MongoStorage
)

from pyLiveMusic.persistence import (
    MemoryRoomRepository, 
    MemoryUserRepository, 
    MongoRoomRepository,
    MongoUserRepository
)

class AppState:

    
    def __init__(self, storage):

        self.storage = None
        self.rooms = None
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
        self.storage = _MemoryStorage()
        self.rooms = RoomManager()
        self.users = MemoryUserRepository()
        self.room_repository = MemoryRoomRepository()

    def MongoDBState(self, storage): 
        self.storage = _MongoStorage(self, storage)
        self.rooms = RoomManager()
        self.users = MongoUserRepository()
        self.room_repository = MongoRoomRepository()

    def RedisState(self, storage):
        self.storage = None
        self.rooms = None
        self.users = None
        self.room_repository = None