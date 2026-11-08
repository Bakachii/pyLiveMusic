from aiohttp import web

from _api._errors import read_json
from _core._core_engine._webrtc.backend import RoomExistsError
from _utils._settings import MAX_ROOM_NAME, ROOM_ID_PATTERN


async def create_room(request):
    request.app["auth"]._verify(request)

    # The room records a fingerprint of the key, never the key itself.
    owner_id = request.app["auth"].owner_id

    data = await read_json(request)

    name = data.get(
        "name",
        "Private Room",
    )

    if (
        not isinstance(name, str)
        or not name.strip()
        or len(name) > MAX_ROOM_NAME
    ):
        raise web.HTTPBadRequest(text="INVALID_ROOM_NAME")

    room_id = data.get("room_id")

    if room_id is not None and (
        not isinstance(room_id, str)
        or not ROOM_ID_PATTERN.match(room_id)
    ):
        raise web.HTTPBadRequest(text="INVALID_ROOM_ID")

    rooms = request.app["state"].rooms

    try:
        room = await rooms.create(
            name=name.strip(),
            controllers={owner_id},
            room_id=room_id,
        )

    except RoomExistsError:
        raise web.HTTPConflict(text="ROOM_EXISTS")

    except ValueError as error:
        raise web.HTTPServiceUnavailable(text=str(error))

    return web.json_response(
        room.state(),
        status=201,
    )

async def get_room(request):
    room_id = request.match_info["room_id"]
    room = request.app["state"].rooms.get(room_id)

    if room is None:
        raise web.HTTPNotFound(text="ROOM_NOT_FOUND")

    return web.json_response(room.state())



async def end_room(request):

    request.app["auth"]._verify(request)

    room_id = request.match_info["room_id"]
    rooms = request.app["state"].rooms
    room = rooms.get(room_id)

    if room is None:
        raise web.HTTPNotFound(text="ROOM_NOT_FOUND")

    await rooms.remove(room_id)

    return web.json_response({"status": "ended"})
