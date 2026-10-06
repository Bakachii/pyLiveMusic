import signal
import asyncio
from pathlib import Path

import aiohttp

from _core._aiohttp._app import _start
from _core._aiohttp._endpoints import (
    Endpoint,
    route_key,
    validate_room_endpoint,
)
from _core._core_func._context import set_client
from _core._core_func._auth._auth import Authentication
from pyLiveMusic._logger import logs

from _utils._settings import STATIC_DIR
from pyLiveMusic.storage.memory import Memory


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
        self._endpoints = {}

        set_client(self)

    def _initialize_players(self):
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

    def add_endpoint(
        self,
        path: str,
        html: str,
        css: str | None = None,
        js: str | None = None,
        root: str | None = None,
    ):
        if not path.startswith("/"):
            raise ValueError(
                f"Endpoint path must start with '/': {path}"
            )

        if path in self._endpoints:
            raise ValueError(
                f"Endpoint already exists: {path}"
            )

        from _api._routes import (
            queue,
            rooms,
            webrtc,
            frontend,
            playback,
        )

        built_in = (
            frontend.static,
            frontend.room,
            rooms.create_room,
            rooms.get_room,
            rooms.end_room,
            playback.pause,
            playback.resume,
            playback.skip,
            playback.volume,
            playback.shuffle,
            playback.repeat,
            playback.ascending,
            playback.descending,
            playback.seek_back,
            playback.seek_front,
            playback.quality,
            queue.get_queue,
            queue.add_track,
            queue.clear_queue,
            queue.remove_track,
            webrtc.offer,
            "/api/rooms/{room_id}/webrtc/candidate",
        )

        normalized = route_key(path)

        for route in built_in:
            if (
                route == frontend.static
                and path.startswith(frontend.static)
            ):
                raise ValueError(
                    f"Endpoint is already assigned by pyLiveMusic: {path}"
                )

            if route_key(route) == normalized:
                raise ValueError(
                    f"Endpoint is already assigned by pyLiveMusic: {path}"
                )

        if any(
            route_key(route) == normalized
            for route in self._endpoints
        ):
            raise ValueError(
                f"Endpoint already exists: {path}"
            )

        html_path = Path(html).resolve()

        css_path = (
            Path(css).resolve()
            if css is not None
            else None
        )

        js_path = (
            Path(js).resolve()
            if js is not None
            else None
        )

        root_path = (
            Path(root).resolve()
            if root is not None
            else None
        )

        if not html_path.is_file():
            raise FileNotFoundError(
                f"HTML file not found: {html_path}"
            )

        if css_path is not None and not css_path.is_file():
            raise FileNotFoundError(
                f"CSS file not found: {css_path}"
            )

        if js_path is not None and not js_path.is_file():
            raise FileNotFoundError(
                f"JavaScript file not found: {js_path}"
            )

        self._endpoints[path] = Endpoint(
            path=path,
            html=html_path,
            css=css_path,
            js=js_path,
            root=root_path,
        )

        return self

    def room_customisation(
        self,
        html: str | None = None,
        css: str | None = None,
        js: str | None = None,
    ):
        from _api._routes import frontend

        if frontend.room in self._endpoints:
            raise ValueError(
                "Room endpoint is already customized."
            )

        html_path = (
            Path(html).resolve()
            if html is not None
            else (STATIC_DIR / "audio.html")
        )

        css_path = (
            Path(css).resolve()
            if css is not None
            else None
        )

        js_path = (
            Path(js).resolve()
            if js is not None
            else None
        )

        if not html_path.is_file():
            raise FileNotFoundError(
                f"HTML file not found: {html_path}"
            )

        if css_path is not None and not css_path.is_file():
            raise FileNotFoundError(
                f"CSS file not found: {css_path}"
            )

        if js_path is not None and not js_path.is_file():
            raise FileNotFoundError(
                f"JavaScript file not found: {js_path}"
            )

        self._endpoints[frontend.room] = Endpoint(
            path=frontend.room,
            html=html_path,
            css=css_path,
            js=js_path,
            room=True,
        )

        return self

    # American spelling alias.
    customise_room = room_customisation

    async def start(self):
        from _api._routes import frontend

        room_endpoint = self._endpoints.get(frontend.room)

        if room_endpoint is not None:
            validate_room_endpoint(room_endpoint)

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
            endpoints=self._endpoints,
        )

        set_client(self)

        if self.player_function:
            self._initialize_players()

        logs.info("Server is running.")

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