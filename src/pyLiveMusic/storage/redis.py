class Redis:
    def __init__(
        self,
        db_url: str | None = None,
        db: int | None = None,
        key_prefix: str | None = None,
    ):

        try:
            import redis.asyncio as redis
        except ImportError as exc:
            raise ImportError(
                "To use the Redis storage, you must install pyLiveMusic via "
                "pip install 'pyLiveMusic[redis]'"
            ) from exc

        self.db_url = db_url or "redis://localhost:6379"
        self.db = db or 0
        self.key_prefix = key_prefix or "pylivemusic"
        self.users = f"{key_prefix}:users"
        self.rooms = f"{key_prefix}:rooms"