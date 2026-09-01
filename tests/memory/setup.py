from pyLiveMusic import pyLiveMusic

server = pyLiveMusic(
    HOST="0.0.0.0",
    PORT=5000,
    AUTH_KEY="124",
)

server.start() 