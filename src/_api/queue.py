from aiohttp import web


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
                "path": item.path,
            }

            for item in room.queue
        ],
    })


async def add_track(request):

    request.app["auth"]._verify(request)

    room = request.app["state"].rooms.get(request.match_info["room_id"])
    if room is None:
        raise web.HTTPNotFound(text="ROOM_NOT_FOUND")

    data = await request.json()

    item = await room.add_track(
        title=data["title"],
        path=data["path"],
    )

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