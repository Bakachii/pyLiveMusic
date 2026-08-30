from aiohttp import web

from pyLiveMusic._api.rooms import (
    create_room,
    end_room,
    get_room,
)

from pyLiveMusic._api.playback import (
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

from pyLiveMusic._api.queue import (
    get_queue,
    add_track,
    remove_track,
    clear_queue,
)

from pyLiveMusic._api.signaling import offer
from pyLiveMusic._utils._settings import STATIC_DIR


async def on_startup(app):
    state = app["state"]
    
    print("Starting server...")
    
    await state.storage.connect()
    await state.rooms.start()


async def on_shutdown(app):
    state = app["state"]

    print("Shutting down...")
    
    await state.rooms.shutdown()
    await state.storage.close()
    
    print("Server stopped")



def create_app(auth, state):
    app = web.Application()
    app["auth"] = auth
    app["state"] = state

    print("Auth Key: " + app["auth"]._get_auth_key())
    
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
