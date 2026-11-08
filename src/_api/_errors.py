from aiohttp import web


ERROR_STATUS = {
    "NOT_PLAYING_ANYTHING_CURRENTLY": 409,
    "INVALID_SEEK_LIMIT": 400,
    "INVALID_SEEK_SECONDS": 400,
    "INVALID_VOLUME": 400,
    "INVALID_REPEAT_MODE": 400,
    "INVALID_PLAY_ORDER": 400,
    "INVALID_AUDIO_QUALITY": 400,
    "TRACK_DURATION_UNKNOWN": 409,
    "QUEUE_FULL": 409,
    "TRACK_UNPLAYABLE": 422,
    "ROOM_FULL": 503,
    "ROOM_EXISTS": 409,
    "TOO_MANY_ROOMS": 503,
}


def json_error(code):
    return web.json_response({"error": code}, status=ERROR_STATUS.get(code, 400))


async def read_json(request) -> dict:
    """The request body as a JSON object, or a clean 400 (never a 500)."""
    try:
        data = await request.json()

    except Exception:
        raise web.HTTPBadRequest(text="INVALID_JSON")

    if not isinstance(data, dict):
        raise web.HTTPBadRequest(text="INVALID_JSON")

    return data


def client_ip(request, trust_proxy=False):
    """The caller's address. X-Forwarded-For is only believed when the
    server is configured to sit behind a reverse proxy."""
    if trust_proxy:
        forwarded = request.headers.get("X-Forwarded-For", "")

        if forwarded:
            return forwarded.split(",")[0].strip() or request.remote

    return request.remote
