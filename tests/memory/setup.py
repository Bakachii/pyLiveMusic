from pyLiveMusic import Client

server = Client(
    HOST="0.0.0.0",
    PORT=5000,
    AUTH_KEY="124",
)

server.start()