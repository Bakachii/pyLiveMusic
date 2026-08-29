from aiohttp import web

from pyLiveMusic.storage import Memory

from pyLiveMusic._state import AppState
from pyLiveMusic._settings import STATIC_DIR
from pyLiveMusic._api.signaling import offer
from pyLiveMusic._webrtc._auth.auth import Authentication



async def on_startup(app):
    state = app["state"]
    
    print("Starting server...")
    
    await state.storage.connect()
    await state.rooms.start()


async def on_shutdown(app):
    state = app["state"]

    print("Shutting down...")
    
    await state.rooms.shutdown()
    await state.db.close()
    
    print("Server stopped")


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
        self.auth =  (
            AUTH_KEY
            if AUTH_KEY is not None
            else Authentication()._get_auth_key()
        )

        self.storage = STORAGE if STORAGE is not None else Memory()
    

    def create_app():
        app = web.Application()
        app["state"] = AppState(self.storage)

        app.on_startup.append(on_startup)
        app.on_shutdown.append(on_shutdown)

        # Frontend


        app.router.add_get("/", lambda request: web.FileResponse(STATIC_DIR / "audio.html"))
        app.router.add_get("/room/{room_id}", lambda request:web.FileResponse(STATIC_DIR / "audio.html"))

        app.router.add_static("/static/", STATIC_DIR)

        # Rooms
        app.router.add_post("/api/rooms", create_room)
        app.router.add_get("/api/rooms/{room_id}", get_room)
        app.router.add_post("/api/rooms/{room_id}/end", end_room)

        # Playback 
        app.router.add_post("/api/rooms/{room_id}/pause", pause)
        app.router.add_post("/api/rooms/{room_id}/resume", resume)
        app.router.add_post("/api/rooms/{room_id}/skip", skip)
        app.router.add_post("/api/rooms/{room_id}/volume", volume)
        app.router.add_post("/api/rooms/{room_id}/shuffle", shuffle)
        app.router.add_post("/api/rooms/{room_id}/repeat", repeat)
        app.router.add_post("/api/rooms/{room_id}/order/ascending", ascending)
        app.router.add_post("/api/rooms/{room_id}/order/descending", descending)
        app.router.add_post("/api/rooms/{room_id}/seek/front", seek_front)
        app.router.add_post("/api/rooms/{room_id}/seek/back", seek_back)
        app.router.add_post("/api/rooms/{room_id}/quality", quality)

        # Queue
        app.router.add_get("/api/rooms/{room_id}/queue", get_queue)
        app.router.add_post("/api/rooms/{room_id}/queue/add", add_track)
        app.router.add_post("/api/rooms/{room_id}/queue/{track_id}/remove", remove_track)
        app.router.add_post("/api/rooms/{room_id}/queue/clear", clear_queue)

        # WebRTC signaling
        app.router.add_post("/api/rooms/{room_id}/webrtc/offer", offer)

        return app

    def start(self):
        app = create_app()
        web.run_app(app, host=self.host, port=self.port)