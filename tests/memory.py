import asyncio

from pyLiveMusic import Client
from pyLiveMusic.storage import Memory


async def main():
    server = Client(
        HOST="0.0.0.0", # Optional server host. Defaults to "0.0.0.0".
        PORT=5000, # Optional server port. Defaults to 8000.
        AUTH_KEY="124", # Optional string authentication key. Generates a random secret if not provided.
        STORAGE=Memory(),
    )
    
    try:
        await server.start() # Start the server after configuring credentials
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass


"""
Memory storage configuration.

Memory:
    Uses Python dictionaries to store data directly in RAM.

    No additional configuration is required.

    Memory is the default storage backend.

    Data is temporary and will be lost when the server
    stops or restarts.
"""