class frontend: 
    home = "/"
    docs = "/docs"

    static = "/static/"
    room = "/room/{room_id}"


BASE_API_ROUTE = "/api/rooms/"

class rooms:
    create_room = "/api/rooms"
    get_room = BASE_API_ROUTE + "{room_id}"
    end_room = BASE_API_ROUTE + "{room_id}/end"

class playback:
    pause = BASE_API_ROUTE + "{room_id}/pause"
    resume = BASE_API_ROUTE + "{room_id}/resume"
    skip = BASE_API_ROUTE + "{room_id}/skip"
    volume = BASE_API_ROUTE + "{room_id}/volume"
    shuffle = BASE_API_ROUTE + "{room_id}/shuffle"
    repeat = BASE_API_ROUTE + "{room_id}/repeat"
    ascending = BASE_API_ROUTE + "{room_id}/ascending"
    descending = BASE_API_ROUTE + "{room_id}/descending"
    seek_back = BASE_API_ROUTE + "{room_id}/seek/back"
    seek_front = BASE_API_ROUTE + "{room_id}/seek/front"
    quality = BASE_API_ROUTE + "{room_id}/quality"

class queue:
    get_queue = BASE_API_ROUTE + "{room_id}/queue"
    add_track = BASE_API_ROUTE + "{room_id}/queue/add"
    clear_queue = BASE_API_ROUTE + "{room_id}/queue/clear"
    remove_track = BASE_API_ROUTE + "{room_id}/queue/{track_id}/remove"

class webrtc:
    offer = BASE_API_ROUTE + "{room_id}/webrtc/offer"