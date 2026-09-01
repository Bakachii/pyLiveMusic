from pyLiveMusic._webrtc.backend import RoomManager

from pyLiveMusic.storage import (
    Memory,
    MongoDB,
    Redis,
    _MongoStorage,
)

from pyLiveMusic.persistence import (
    MemoryRoomRepository,
    MemoryUserRepository,
    MongoRoomRepository,
    MongoUserRepository,
)


class _core_state:

    def __init__(self):
        self.rooms = None
        self.storage = None
        self.users = None
        self.room_repository = None

    def MemoryState(self, storage):
        self.storage = storage.storage
        self.users = MemoryUserRepository(self.storage.users)
        self.room_repository = MemoryRoomRepository(self.storage.rooms)
        self.rooms = RoomManager(self.room_repository)

    def MongoDBState(self, storage):
        self.storage = _MongoStorage(
            storage.db_url,
            storage.db_name,
            storage.user_collection,
            storage.room_collection,
        )

        self.users = MongoUserRepository(self.storage.users)
        self.room_repository = MongoRoomRepository(self.storage.rooms)
        self.rooms = RoomManager(self.room_repository)

    def RedisState(self, storage):
        raise NotImplementedError("Redis storage is not implemented yet")


class AppState:

    def __init__(self, storage):
        state_container = _core_state()

        if isinstance(storage, Memory):
            state_container.MemoryState(storage)

        elif isinstance(storage, MongoDB):
            state_container.MongoDBState(storage)

        elif isinstance(storage, Redis):
            state_container.RedisState(storage)

        else:
            raise TypeError("Unsupported storage type")

        self.rooms = state_container.rooms
        self.storage = state_container.storage
        self.users = state_container.users
        self.room_repository = state_container.room_repository
