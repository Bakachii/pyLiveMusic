from pyLiveMusic import Client
from pyLiveMusic.storage import Redis

db_url = "redis://localhost:6379"
db = 0
key_prefix = "pylivemusic"

server = Client(
    HOST="0.0.0.0", # Optional server host. Defaults to "0.0.0.0".
    PORT=5000, # Optional server port. Defaults to 8000.
    AUTH_KEY="124", # Optional string authentication key. Generates a random secret if not provided.
    STORAGE=Redis(
        db_url=db_url, 
        db=db, 
        key_prefix=key_prefix,
    ),
)

"""
Redis storage configuration.

db_url:
    The Redis connection URL. This is required when using Redis storage.

    Example:
        redis://localhost:6379

db:
    The Redis database number to use.
    This is optional and defaults to 0.

    Example:
        Redis(db_url=DB_URL, db=1)

key_prefix:
    A prefix added to pyLiveMusic Redis keys.
    This is optional and defaults to "pylivemusic".

    Example:
        Redis(
            db_url=DB_URL,
            key_prefix="my_music_app",
        )

Only db_url is required. The db and key_prefix
parameters are optional.
"""


server.start() # Start the server after configuring credentials