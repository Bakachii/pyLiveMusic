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
}


def json_error(code):
    return web.json_response({"error": code}, status=ERROR_STATUS.get(code, 400))