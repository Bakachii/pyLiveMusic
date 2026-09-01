from pyLiveMusic._core._core_func._data_config import _core_state

from pyLiveMusic.storage import Memory, MongoDB, Redis


class _data_state:

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
