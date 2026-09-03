from pyLiveMusic import Client

server = Client() # Create and configure the pyLiveMusic server.

"""
Client configuration:

HOST:
    Optional. The host address where the server will listen.
    Defaults to "0.0.0.0".

PORT:
    Optional. The port where the server will listen.
    Defaults to 8000.

AUTH_KEY:
    Optional string used to authenticate requests.
    If not provided, a random secret key will be generated.

STORAGE:
    Optional. Defines the storage backend used by the server.
    Available options are Memory, MongoDB, and Redis.
    Defaults to Memory if not specified.

    For MongoDB or Redis, import the storage backend from:
        from pyLiveMusic.storage import Memory, MongoDB, Redis

If no configuration is provided, pyLiveMusic will use:
    HOST     ->"0.0.0.0"
    PORT     -> 8000
    AUTH_KEY -> Randomly generated secret
    STORAGE  -> Memory
"""

server.start() # Start the pyLiveMusic server.