from _core._core_func._context import get_client


class Playback:

    def __init__(self):
        self.client = get_client()

    async def pause(self):
        pass

    async def resume(self):
        pass

    async def skip(self):
        pass

    async def volume(self):
        pass

    async def mute(self):
        pass

    async def shuffle(self):
        pass

    async def repeat(self):
        pass

    async def order(self):
        pass

    async def seek(self):
        pass

    async def quality(self):
        pass


