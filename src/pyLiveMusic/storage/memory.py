from pyLiveMusic._core._database.memory._storage import _MemoryStorage

class Memory:
    def __init__(self):
        self.storage = _MemoryStorage()

    async def connect(self):
        await self.storage.connect()

    async def close(self):
        await self.storage.close()