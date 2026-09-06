import signal
import asyncio

import aiohttp

from pyLiveMusic.storage.memory import Memory

from _core._aiohttp._app import _start
from _core._core_func._context import set_client
from _core._core_func._auth._auth import Authentication


class Client:

    def __init__(
        self,
        HOST: str = "0.0.0.0",
        PORT: int = 8000,
        AUTH_KEY: str | None = None,
        STORAGE=None,
        player_function: bool = False,
    ):
        self.host = HOST
        self.port = PORT

        self.base_url = f"http://{HOST}:{PORT}"

        self.auth = Authentication(AUTH_KEY)
        self.storage = STORAGE if STORAGE is not None else Memory()

        self.player_function = player_function

        self.http = None
        self.runner = None
        self._players = {}

        set_client(self)


    def _initialize_players(self):
        """
        Initialize all pyLiveMusic player classes.

        This only creates the objects.
        It does not execute any player actions.
        """

        from pyLiveMusic.player import (
            Room,
            Queue,
            Playback,
        )

        player_classes = (
            Room,
            Queue,
            Playback,
        )

        for player_class in player_classes:
            self._players[player_class] = player_class()


    def get(self, *classes):
        if not self.player_function:
            raise RuntimeError(
                "Player functions are disabled. "
                "Create Client(player_function=True) "
                "to use client.get()."
            )

        instances = []

        for class_ in classes:
            instance = self._players.get(class_)

            if instance is None:
                raise RuntimeError(
                    f"{class_.__name__} has not been initialized."
                )

            instances.append(instance)

        if len(instances) == 1:
            return instances[0]

        return tuple(instances)


    async def start(self):

        self.http = aiohttp.ClientSession(
            base_url=self.base_url,
            headers={
                "Authorization": (
                    f"Bearer {self.auth._get_auth_key()}"
                )
            },
        )

        self.runner = await _start(
            host=self.host,
            port=self.port,
            auth=self.auth,
            storage=self.storage,
        )

        set_client(self)

        if self.player_function:
            self._initialize_players()

        print("Server is running.")

        return self


    async def run_until_disconnect(self):
        stop_event = asyncio.Event()
        loop = asyncio.get_running_loop()

        def signal_handler():
            stop_event.set()

        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, signal_handler)

        try:
            await stop_event.wait()

        finally:
            await self.stop()


    async def stop(self):

        if self.runner is not None:
            await self.runner.cleanup()
            self.runner = None

        if self.http is not None:
            await self.http.close()
            self.http = None

        self._players.clear()