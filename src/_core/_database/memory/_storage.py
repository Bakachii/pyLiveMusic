from pyLiveMusic._logger import logs

class _MemoryStorage:
    def __init__(self):
        self.users = {}
        self.rooms = {}

    async def connect(self):
        logs.info("Memory storage initialized")

    async def close(self):
        self.users.clear()
        self.rooms.clear()

        logs.info("Memory storage cleared")
