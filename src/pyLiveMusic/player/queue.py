from _api._routes import BASE_API_ROUTE
from _core._core_func._context import get_client


class Queue:

    def __init__(self):
        self.client = get_client()
        self.room_id = None

    async def get_queue(self, room_id: str):
        response = await self.client.http.get(BASE_API_ROUTE + f"{room_id}/queue")

        response.raise_for_status()
        return await response.json()

    async def clear_queue(self, room_id: str):
        response = await self.client.http.delete(BASE_API_ROUTE + f"{room_id}/queue/clear")

        response.raise_for_status()
        return await response.json()

    async def add_track(
        self,
        room_id: str,
        title: str,
        path: str,
    ):
        data = {
            "title": title,
            "path": path,
        }

        response = await self.client.http.post(BASE_API_ROUTE + f"{room_id}/queue/add", json=data)

        response.raise_for_status()
        return await response.json()

    async def remove_track(
        self,
        room_id: str,
        track_id: str,
    ):
        response = await self.client.http.delete(BASE_API_ROUTE + f"{room_id}/queue/{track_id}/remove")

        response.raise_for_status()
        return await response.json()