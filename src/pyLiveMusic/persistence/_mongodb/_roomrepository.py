class MongoRoomRepository:

    def __init__(self, collection):
        
        self.collection = collection

    async def create(
        self,
        room_id,
        name,
        controllers,
    ):

        document = {
            "_id": room_id,
            "name": name,
            "controllers": controllers,
        }

        await self.collection.insert_one(document)

        return document

    async def get(self, room_id):
        return await self.collection.find_one({"_id": room_id})

    async def delete(self, room_id):
        await self.collection.delete_one({"_id": room_id})