class _RedisStorage:

    def __init__(
        self,
        db_url: str,
        db: int = 0,
        key_prefix: str = "pylivemusic",
    ):
        try:
            import redis.asyncio as redis
        except ImportError as exc:
            raise ImportError(
                "To use the Redis storage, you must install pyLiveMusic via "
                "pip install 'pyLiveMusic[redis]'"
            ) from exc

        self.client = redis.Redis.from_url(
            db_url,
            db=int(db),
            decode_responses=True,
        )

        self.key_prefix = key_prefix

    async def connect(self):
        await self.client.ping()
        print("Redis connected")

    async def close(self):
        await self.client.aclose()
        print("Redis disconnected")