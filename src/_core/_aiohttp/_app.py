import os
import time
import asyncio

from aiohttp import web

from pyLiveMusic._logger import logs

from _api._routes import (
    queue,
    rooms,
    server,
    webrtc,
    frontend,
    playback,
)
from _api.rooms import (
    create_room,
    end_room,
    get_room,
)

from _api.playback import (
    pause,
    resume,
    skip,
    volume,
    shuffle,
    repeat,
    ascending,
    descending,
    seek_front,
    seek_back,
    quality,
)

from _api.queue import (
    get_queue,
    add_track,
    remove_track,
    clear_queue,
)

from _utils._settings import (
    MAX_BODY_BYTES,
    STATIC_DIR,
    STATS_LOG_EVERY,
    ServerOptions,
)
from _core._core_func._ice import browser_ice_servers
from _core._core_engine._webrtc.signaling import (
    offer,
    candidate,
)
from _core._core_func._state._data_state import _data_state
from _core._aiohttp._endpoints import register_endpoint


def _process_stats(app):
    """Numbers that grow when something leaks: open files, tasks, memory."""
    state = app["state"]

    stats = {
        "uptime_seconds": int(time.time() - app["started_at"]),
        "rooms": len(state.rooms.rooms),
        "peers": state.rooms.total_peers(),
        "asyncio_tasks": len(asyncio.all_tasks()),
        "open_files": None,
        "open_files_limit": None,
        "memory_mb": None,
    }

    try:
        stats["open_files"] = len(os.listdir("/proc/self/fd"))

        with open("/proc/self/statm") as file:
            pages = int(file.read().split()[1])

        stats["memory_mb"] = round(pages * os.sysconf("SC_PAGE_SIZE") / 1e6, 1)

    except OSError:
        pass

    try:
        import resource

        stats["open_files_limit"] = resource.getrlimit(resource.RLIMIT_NOFILE)[0]

    except Exception:
        pass

    return stats


async def _monitor(app):
    """Logs the numbers above regularly, so a slow leak shows up in the logs
    long before it takes the server down."""
    while True:
        await asyncio.sleep(STATS_LOG_EVERY)

        stats = _process_stats(app)
        logs.info("[STATS] " + " ".join(f"{k}={v}" for k, v in stats.items()))

        used, limit = stats["open_files"], stats["open_files_limit"]

        if used and limit and used > limit * 0.8:
            logs.warning(
                f"[STATS] {used}/{limit} file descriptors in use: "
                "the server will soon stop accepting connections"
            )


async def on_startup(app):
    state = app["state"]

    logs.info("Starting server...")

    await state.storage.connect()
    await state.rooms.start()

    app["monitor"] = asyncio.create_task(_monitor(app))


async def on_shutdown(app):
    state = app["state"]

    logs.info("Shutting down...")

    monitor = app.get("monitor")

    if monitor:
        monitor.cancel()

    await state.rooms.shutdown()
    await state.storage.close()

    logs.info("Server stopped")


async def health(request):
    request.app["auth"]._verify(request)

    return web.json_response(_process_stats(request.app))


async def webrtc_config(request):
    """ICE servers for the browser (STUN, and TURN with short-lived
    credentials when configured)."""
    return web.json_response(
        {"iceServers": browser_ice_servers(request.app["options"])},
        headers={"Cache-Control": "no-store"},
    )


@web.middleware
async def _middleware(request, handler):
    try:
        response = await handler(request)

    except web.HTTPException as error:
        _harden(request, error)
        raise

    _harden(request, response)

    # Compress text responses (JSON, custom pages). Streams (SSE) and files
    # are left alone.
    if (
        type(response) is web.Response
        and "Content-Encoding" not in response.headers
        and isinstance(response.body, (bytes, bytearray))
        and len(response.body) > 1024
        and (response.content_type or "").startswith(
            ("text/", "application/json", "application/javascript")
        )
    ):
        response.enable_compression()

    return response


def _harden(request, response):
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("Referrer-Policy", "no-referrer")

    if request.path.startswith("/api/"):
        response.headers.setdefault("Cache-Control", "no-store")


def create_app(auth, state, endpoints=None, options=None):
    options = options or ServerOptions()

    app = web.Application(
        client_max_size=MAX_BODY_BYTES,
        middlewares=[_middleware],
    )
    app["auth"] = auth
    app["state"] = state
    app["options"] = options
    app["started_at"] = time.time()

    # Rooms read their limits and ICE settings from here, and record the
    # key's fingerprint (never the key) as owner.
    state.rooms.options = options
    state.rooms.owner_id = auth.owner_id

    # Never write the key to the logs: it is a password, and often a bot
    # token. A generated key is available as `client.auth_key`.
    if auth.generated:
        logs.warning(
            "No AUTH_KEY given: a random key was generated for this run "
            "(read it from client.auth_key)."
        )
    else:
        logs.info(f"API authentication enabled (key fingerprint {auth.owner_id})")
    
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)

    # Frontend
    endpoints = endpoints or {}

    if frontend.room not in endpoints:
        app.router.add_get(
            frontend.room,
            lambda request: web.FileResponse(
                STATIC_DIR / "audio.html"
            ),
        )

    app.router.add_static(frontend.static, STATIC_DIR)

    for endpoint in endpoints.values():
        register_endpoint(app, endpoint)

    # Rooms
    app.router.add_get(rooms.get_room, get_room)
    app.router.add_post(rooms.end_room, end_room)
    app.router.add_post(rooms.create_room, create_room)

    # Playback 
    app.router.add_post(playback.pause, pause)
    app.router.add_post(playback.resume, resume)
    app.router.add_post(playback.skip, skip)
    app.router.add_post(playback.volume, volume)
    app.router.add_post(playback.shuffle, shuffle)
    app.router.add_post(playback.repeat, repeat)
    app.router.add_post(playback.ascending, ascending)
    app.router.add_post(playback.descending, descending)
    app.router.add_post(playback.seek_front, seek_front)
    app.router.add_post(playback.seek_back, seek_back)
    app.router.add_post(playback.quality, quality)

    # Queue
    app.router.add_get(queue.get_queue, get_queue)
    app.router.add_post(queue.add_track, add_track)
    app.router.add_post(queue.remove_track, remove_track)
    app.router.add_post(queue.clear_queue, clear_queue)

    # Server
    app.router.add_get(server.health, health)
    app.router.add_get(webrtc.config, webrtc_config)

    # WebRTC signaling
    app.router.add_post(webrtc.offer, offer)
    app.router.add_post(
        "/api/rooms/{room_id}/webrtc/candidate",
        candidate,
    )

    return app



async def _start(host, port, auth, storage, endpoints=None, options=None):
    app = create_app(
        auth=auth,
        state=_data_state(storage),
        endpoints=endpoints,
        options=options,
    )

    runner = web.AppRunner(app)

    await runner.setup()

    site = web.TCPSite(
        runner,
        host,
        port,
    )

    await site.start()

    logs.info(f"Server started on http://{host}:{port}")

    return runner