from _core._core_func._context import get_client


class Room:
    
    def __init__(self):
        self.client = get_client()

    async def create_room(self):
        pass 

    async def get_room(self):
        pass

    async def end_room(self):
        pass