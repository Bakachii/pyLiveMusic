import asyncio

from pyLiveMusic import Client

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

async def main():
    # Initialize the client with host and port
    server = Client(HOST="0.0.0.0", PORT=8000)
    
    try:
        await server.start() # Start the server after configuring credentials
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass