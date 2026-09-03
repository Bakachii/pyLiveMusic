from _core._core_engine._webrtc.backend import RoomManager

from _core._database.mongo._storage import _MongoStorage
from _core._database.redis._storage import _RedisStorage
from _core._database.mongo._repo import MongoRoomRepository, MongoUserRepository
from _core._database.memory._repo import MemoryRoomRepository, MemoryUserRepository
from _core._database.redis._repo import RedisRoomRepository, RedisUserRepository


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
        self.storage = _RedisStorage(
            storage.db_url,
            storage.db,
            storage.key_prefix,
        )
        self.users = RedisUserRepository(self.storage.client, self.storage.key_prefix)
        self.room_repository = RedisRoomRepository(self.storage.client, self.storage.key_prefix)
        self.rooms = RoomManager(self.room_repository)