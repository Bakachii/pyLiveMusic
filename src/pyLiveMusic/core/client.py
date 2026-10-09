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

    # ------------------------------------------------------------------
    # Endpoints
    # ------------------------------------------------------------------

    @staticmethod
    def _resolve_file(
        value: str | None,
        label: str,
        default: Path | None = None,
    ) -> Path | None:
        """Absolute path of an existing file (or `default` / None)."""
        if value is None and default is None:
            return None

        path = Path(value).resolve() if value is not None else default

        if not path.is_file():
            raise FileNotFoundError(f"{label} file not found: {path}")

        return path

    def _check_path_available(self, path: str) -> None:
        """Raises if `path` is invalid, built in, or already registered."""
        if not isinstance(path, str) or not path.startswith("/"):
            raise ValueError(
                f"Endpoint path must start with '/': {path}"
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

        if path in self._endpoints or any(
            route_key(route) == normalized
            for route in self._endpoints
        ):
            raise ValueError(
                f"Endpoint already exists: {path}"
            )

    def add_endpoint(
        self,
        path: str,
        html: str | None = None,
        css: str | None = None,
        js: str | None = None,
        root: str | None = None,
        *,
        get=None,
        post=None,
    ):
        """Register a route.

        Page endpoint (as before):
            client.add_endpoint("/home", html="home/index.html",
                                css="home/style.css", js="home/script.js")

        API endpoint (no page): pass async handlers instead of html.
            client.add_endpoint("/botinfo", get=bot_info)
            client.add_endpoint("/presence/{room}/join", post=join)

        A handler is `async def handler(request) -> aiohttp.web.Response`.
        `{name}` parts of the path are read with request.match_info["name"].
        Routes are registered in call order.
        """
        if html is None and get is None and post is None:
            raise ValueError(
                "add_endpoint needs a page (html=) "
                "or a handler (get= / post=)."
            )

        if html is None and any(
            value is not None for value in (css, js, root)
        ):
            raise ValueError(
                "css=, js= and root= belong to a page: pass html= as well."
            )

        for name, handler in (("get", get), ("post", post)):
            if handler is not None and not callable(handler):
                raise TypeError(
                    f"{name}= must be an async function taking (request), "
                    f"got {handler!r}"
                )

        self._check_path_available(path)

        html_path = self._resolve_file(html, "HTML")
        css_path = self._resolve_file(css, "CSS")
        js_path = self._resolve_file(js, "JavaScript")

        root_path = (
            Path(root).resolve()
            if root is not None
            else None
        )

        self._endpoints[path] = Endpoint(
            path=path,
            html=html_path,
            css=css_path,
            js=js_path,
            root=root_path,
            get=get,
            post=post,
        )

        return self

    def add_api(self, path: str, *, get=None, post=None):
        """Shortcut for an endpoint without a page.

            client.add_api("/botinfo", get=bot_info)
            client.add_api("/presence/{room}/join", post=join)
        """
        if get is None and post is None:
            raise ValueError("add_api needs get= and/or post=.")

        return self.add_endpoint(path, get=get, post=post)

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

        html_path = self._resolve_file(
            html,
            "HTML",
            default=STATIC_DIR / "audio.html",
        )

        css_path = self._resolve_file(css, "CSS")
        js_path = self._resolve_file(js, "JavaScript")

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