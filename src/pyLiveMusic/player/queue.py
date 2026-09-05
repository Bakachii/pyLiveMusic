from _core._core_func._context import get_client


class Queue:

    def __init__(self):
        self.client = get_client()

    async def get_queue(self):
        pass 
    
    async def clear_queue(self):
        pass
    
    async def add_track(self):
        pass

    async def remove_track(self):
        pass
