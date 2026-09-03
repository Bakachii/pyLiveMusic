from aiohttp import web


async def offer(request):
    room_id = request.match_info["room_id"]
    room = request.app["state"].rooms.get(room_id)

    if room is None:
        raise web.HTTPNotFound(text="Room not found")

    data = await request.json()
    peer = await room.add_peer()

    try:
        answer = await room.offer(peer, data["sdp"])
    except Exception:
        await room.remove_peer(peer)

        raise

    return web.json_response({
        "type": answer.type,
        "sdp": answer.sdp,
    })