from aiohttp import web

from pyLiveMusic.storage.memory import Memory

from pyLiveMusic._utils._app import create_app
from pyLiveMusic._utils.auth import Authentication
from pyLiveMusic._core._core_func._state._data_state import _data_state


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
            state=_data_state(self.storage)
        )

        web.run_app(
            app, 
            host=self.host, 
            port=self.port
        )