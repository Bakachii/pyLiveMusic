class MongoUserRepository:

    def __init__(self, collection):

        self.collection = collection

    async def get(self, user_id):
        return await self.collection.find_one({"_id": user_id})

    async def create(
        self,
        user_id,
        username,
    ):

        document = {"_id": user_id, "username": username}

        await self.collection.insert_one(document)

        return document