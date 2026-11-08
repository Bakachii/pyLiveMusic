from pathlib import Path

from aiohttp import web

from _api._errors import json_error, read_json
from _utils._settings import MAX_PATH, MAX_TITLE


def _media_path(raw, options):
    """A real file, optionally restricted to the configured folders.

    The path is handed to the audio decoder, so it must never be an
    arbitrary string chosen by a caller.
    """
    if (
        not isinstance(raw, str)
        or not raw
        or len(raw) > MAX_PATH
        or "\x00" in raw
    ):
        raise web.HTTPBadRequest(text="INVALID_PATH")

    try:
        path = Path(raw).resolve()

        if not path.is_file():
            raise web.HTTPBadRequest(text="INVALID_PATH")

    except OSError:
        raise web.HTTPBadRequest(text="INVALID_PATH")

    if options.media_dirs and not any(
        path.is_relative_to(folder)
        for folder in options.media_dirs
    ):
        raise web.HTTPBadRequest(text="INVALID_PATH")

    return str(path)


async def get_queue(request):

    room = request.app["state"].rooms.get(request.match_info["room_id"])
    if room is None:
        raise web.HTTPNotFound(text="ROOM_NOT_FOUND")

    return web.json_response({
        "room_id": room.id,
        "current":
            (
                {
                    "id": room.current.id,
                    "title": room.current.title,
                }
                if room.current
                else None
            ),

        "queue": [
            {
                "id": item.id,
                "title": item.title,
                **(
                    {"path": item.path}
                    if request.app["auth"].is_valid(request)
                    else {}
                ),
            }

            for item in room.queue
        ],
    })


async def add_track(request):

    request.app["auth"]._verify(request)

    room = request.app["state"].rooms.get(request.match_info["room_id"])
    if room is None:
        raise web.HTTPNotFound(text="ROOM_NOT_FOUND")

    data = await read_json(request)

    title = data.get("title")

    if (
        not isinstance(title, str)
        or not title.strip()
        or len(title) > MAX_TITLE
    ):
        raise web.HTTPBadRequest(text="INVALID_TITLE")

    path = _media_path(
        data.get("path"),
        request.app["options"],
    )

    try:
        item = await room.add_track(
            title=title.strip(),
            path=path,
        )

    except ValueError as error:
        return json_error(str(error))

    return web.json_response(
        {
            "id": item.id,
            "title": item.title,
        },
        status=201,
    )


async def remove_track(request):

    request.app["auth"]._verify(request)

    room = request.app["state"].rooms.get(request.match_info["room_id"])
    if room is None:
        raise web.HTTPNotFound(text="ROOM_NOT_FOUND")

    track_id = request.match_info["track_id"]
    before = len(room.queue)

    room.queue = [
        item
        for item in room.queue
        if item.id != track_id
    ]

    if len(room.queue) == before:
        raise web.HTTPNotFound(text="TRACK_NOT_FOUND")

    return web.json_response(
        {
            "queue": [
                {
                    "id": item.id,
                    "title": item.title,
                }

                for item in room.queue
            ]
        }
    )


async def clear_queue(request):
    request.app["auth"]._verify(request)
    
    room = request.app["state"].rooms.get(request.match_info["room_id"])
    if room is None:
        raise web.HTTPNotFound(text="ROOM_NOT_FOUND")

    room.queue.clear()

    if room.current is None:
        room.schedule_delete()

    return web.json_response({
        "queue": []
    })