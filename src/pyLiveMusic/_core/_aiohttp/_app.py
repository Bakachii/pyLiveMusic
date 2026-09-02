from aiohttp import web

from pyLiveMusic._api._routes import (
    queue,
    rooms,
    webrtc,
    frontend,
    playback,
)
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

from pyLiveMusic._utils._settings import STATIC_DIR
from pyLiveMusic._core._core_engine._webrtc.signaling import offer
from pyLiveMusic._core._core_func._state._data_state import _data_state


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
    app.router.add_get(frontend.home, lambda request: web.FileResponse(STATIC_DIR / "audio.html"))
    app.router.add_get(frontend.room, lambda request:web.FileResponse(STATIC_DIR / "audio.html"))

    app.router.add_static(frontend.static, STATIC_DIR)

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

    # WebRTC signaling
    app.router.add_post(webrtc.offer, offer)

    return app

def _start(host, port, auth, storage):
    app = create_app(auth=auth, state=_data_state(storage))
    web.run_app(app, host=host, port=port)