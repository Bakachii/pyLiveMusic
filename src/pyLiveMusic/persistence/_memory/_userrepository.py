class MemoryUserRepository:

    def __init__(self):
        self.users = {}

    async def get(self, user_id):
        return self.users.get(user_id)

    async def create(
        self,
        user_id,
        username,
    ):
        document = {
            "_id": user_id,
            "username": username
        }

        self.users[user_id] = document

        return document