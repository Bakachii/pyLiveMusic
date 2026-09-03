from pyLiveMusic.storage.memory import Memory

from _core._aiohttp._app import _start
from _core._core_func._auth._auth import Authentication

class Client:

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
        _start(host=self.host, port=self.port, auth=self.auth, storage=self.storage)
