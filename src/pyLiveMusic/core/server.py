from aiohttp import web

from pyLiveMusic.storage import Memory

from pyLiveMusic._utils._state import AppState
from pyLiveMusic._utils._app import create_app
from pyLiveMusic._utils.auth import Authentication

class pyLiveMusic:

    def __init__(
        self,
        HOST: str = "0.0.0.0",
        PORT: int = 8000,
        AUTH_KEY: str | None = None,
        STORAGE = None,
    ):

        self.host = HOST
        self.port = PORT
        self.auth =  Authentication(AUTH_KEY)

        self.storage = STORAGE if STORAGE is not None else Memory()
    

    def start(self):
        app = create_app(
            auth=self.auth, 
            state=AppState(self.storage)
        )

        web.run_app(
            app, 
            host=self.host, 
            port=self.port
        )