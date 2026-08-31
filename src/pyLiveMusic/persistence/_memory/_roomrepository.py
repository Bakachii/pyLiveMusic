class MemoryRoomRepository:

    def __init__(self, rooms):
        self.rooms = rooms

    async def create(self, room_id, name, controllers):
        document = {
            "_id": room_id,
            "name": name,
            "controllers": controllers
        }

        self.rooms[room_id] = document

        return document

    async def get(self, room_id):
        return self.rooms.get(room_id)

    async def delete(self, room_id):
        self.rooms.pop(room_id, None)