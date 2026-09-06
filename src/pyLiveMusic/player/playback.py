from _api._routes import BASE_API_ROUTE, playback
from _core._core_func._context import get_client


class Playback:

    def __init__(self):
        self.client = get_client()
        self.room_id = None

    async def pause(self, room_id: str):
        response = await self.client.http.post(BASE_API_ROUTE + f"{room_id}/pause")

        response.raise_for_status()
        return await response.json()

    async def resume(self, room_id: str):
        response = await self.client.http.post(BASE_API_ROUTE + f"{room_id}/resume")

        response.raise_for_status()
        return await response.json()

    async def skip(self, room_id: str):
        response = await self.client.http.post(BASE_API_ROUTE + f"{room_id}/skip")
        
        response.raise_for_status()
        return await response.json()

    async def volume(
        self,
        room_id: str,
        volume: float,
    ):
        response = await self.client.http.post(BASE_API_ROUTE + f"{room_id}/volume", json={"volume": volume})

        response.raise_for_status()
        return await response.json()

    async def mute(self, room_id: str):
        response = await self.client.http.post(BASE_API_ROUTE + f"{room_id}/mute")

        response.raise_for_status()
        return await response.json()

    async def shuffle(
        self,
        room_id: str,
        enabled: bool,
    ):
        response = await self.client.http.post(BASE_API_ROUTE + f"{room_id}/shuffle", json={"enabled": enabled})

        response.raise_for_status()
        return await response.json()

    async def repeat(
        self,
        room_id: str,
        mode: str = "once",
    ):
        response = await self.client.http.post(BASE_API_ROUTE + f"{room_id}/repeat", json={"mode": mode})

        response.raise_for_status()
        return await response.json()

    async def order(
        self,
        room_id: str,
        direction: str = "ascending",
    ):
        response = await self.client.http.post(BASE_API_ROUTE + f"{room_id}/{direction}")

        response.raise_for_status()
        return await response.json()

    async def seek(
        self,
        room_id: str,
        seconds: float,
        direction: str = "front",
    ):
        response = await self.client.http.post(BASE_API_ROUTE + f"{room_id}/seek/{direction}", json={"seconds": seconds})

        response.raise_for_status()
        return await response.json()

    async def quality(
        self,
        room_id: str,
        quality: str,
    ):
        response = await self.client.http.post(BASE_API_ROUTE + f"{room_id}/quality", json={"quality": quality})
        response.raise_for_status()
        return await response.json()