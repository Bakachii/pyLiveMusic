from _api._routes import BASE_API_ROUTE, rooms
from _core._core_func._context import get_client


class Room:

    def __init__(self):
        self.client = get_client()
        self.room_id = None

    async def create(
        self,
        name: str = "Private Room",
        room_id: str | None = None,
    ):
        data = {
            "name": name,
            "room_id": room_id,
        }

        response = await self.client.http.post(
            rooms.create_room,
            json=data,
        )

        response.raise_for_status()

        data = await response.json()
        self.room_id = data["room_id"]

        return data

    async def get(self, room_id: str):
        response = await self.client.http.get(BASE_API_ROUTE + f"{room_id}")

        response.raise_for_status()
        return await response.json()


    async def end(self, room_id: str):
        response = await self.client.http.post(BASE_API_ROUTE + f"{room_id}/end")

        response.raise_for_status()
        return await response.json()