class _MemoryStorage:
    def __init__(self):
        self.users = {}
        self.rooms = {}

    async def connect(self):
        print("Memory storage initialized")

    async def close(self):
        self.users.clear()
        self.rooms.clear()

        print("Memory storage cleared")


class Memory:
    def __init__(self):
        self.storage = _MemoryStorage()

    async def connect(self):
        await self.storage.connect()

    async def close(self):
        await self.storage.close()