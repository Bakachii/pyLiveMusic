# pyLiveMusic API — cURL Reference

This document contains the available HTTP API commands for testing `pyLiveMusic`.

## Server

Default server:

```text
http://localhost:8000
```

Authentication:

```text
Authorization: Bearer key
```

> Replace `key` with the authentication key printed by your server.

---

# 1. Room API

## Create a room

Creates a new live room and persists its room data through the configured repository.

```bash
curl -X POST http://localhost:8000/api/rooms \
  -H "Authorization: Bearer 124" \
  -H "Content-Type: application/json" \
  -d '{"name":"My Room"}'
```

Example response:

```json
{
  "room_id": "bdf36a19a0a9",
  "name": "My Room",
  "playing": false,
  "position": 0.0,
  "duration": 0.0,
  "volume": 1.0,
  "quality": "high",
  "shuffle": false,
  "repeat": "none",
  "order": "ascending",
  "current": null,
  "queue": []
}
```

Save the returned room ID:

```bash
ROOM_ID="bdf36a19a0a9"
```

---

## Get a room

Returns the current live runtime state of a room.

```bash
curl http://localhost:8000/api/rooms/$ROOM_ID
```

Or directly:

```bash
curl http://localhost:8000/api/rooms/bdf36a19a0a9
```

---

## End a room

Ends the live room and removes its persisted room record.

```bash
curl -X POST http://localhost:8000/api/rooms/$ROOM_ID/end \
  -H "Authorization: Bearer 124"
```

Example response:

```json
{
  "status": "ended"
}
```

---

# 2. Queue API

## Get the queue

```bash
curl http://localhost:8000/api/rooms/$ROOM_ID/queue
```

Example:

```json
{
  "room_id": "bdf36a19a0a9",
  "current": {
    "id": "8d2d...",
    "title": "My Song"
  },
  "queue": []
}
```

---

## Add a track

Add an audio file to the room queue.

```bash
curl -X POST http://localhost:8000/api/rooms/$ROOM_ID/queue/add \
  -H "Authorization: Bearer 124" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My Song",
    "path": "/home/bakachii/stuffs/codes/python/pyLiveMusic/audio.mp3"
  }'
```

Example response:

```json
{
  "id": "8d2d...",
  "title": "My Song"
}
```

Save the returned track ID:

```bash
TRACK_ID="8d2d..."
```

> If there is no current track, the first added track may start playing immediately instead of remaining only in the queue.

---

## Remove a queued track

```bash
curl -X POST http://localhost:8000/api/rooms/$ROOM_ID/queue/$TRACK_ID/remove \
  -H "Authorization: Bearer 124"
```

Example:

```bash
curl -X POST http://localhost:8000/api/rooms/bdf36a19a0a9/queue/8d2d1234/remove \
  -H "Authorization: Bearer 124"
```

> This endpoint removes a queued item. It is not intended to remove the currently playing track.

---

## Clear the queue

```bash
curl -X POST http://localhost:8000/api/rooms/$ROOM_ID/queue/clear \
  -H "Authorization: Bearer 124"
```

---

# 3. Playback API

## Pause

```bash
curl -X POST http://localhost:8000/api/rooms/$ROOM_ID/pause \
  -H "Authorization: Bearer 124"
```

---

## Resume

```bash
curl -X POST http://localhost:8000/api/rooms/$ROOM_ID/resume \
  -H "Authorization: Bearer 124"
```

---

## Skip

Skips the currently playing track and moves to the next available track.

```bash
curl -X POST http://localhost:8000/api/rooms/$ROOM_ID/skip \
  -H "Authorization: Bearer 124"
```

---

# 4. Volume

Volume is represented as a value from `0` to `1`.

## 50% volume

```bash
curl -X POST http://localhost:8000/api/rooms/$ROOM_ID/volume \
  -H "Authorization: Bearer 124" \
  -H "Content-Type: application/json" \
  -d '{"volume":0.5}'
```

## 100% volume

```bash
curl -X POST http://localhost:8000/api/rooms/$ROOM_ID/volume \
  -H "Authorization: Bearer 124" \
  -H "Content-Type: application/json" \
  -d '{"volume":1.0}'
```

## Mute

```bash
curl -X POST http://localhost:8000/api/rooms/$ROOM_ID/volume \
  -H "Authorization: Bearer 124" \
  -H "Content-Type: application/json" \
  -d '{"volume":0}'
```

---

# 5. Shuffle

## Enable shuffle

```bash
curl -X POST http://localhost:8000/api/rooms/$ROOM_ID/shuffle \
  -H "Authorization: Bearer 124" \
  -H "Content-Type: application/json" \
  -d '{"enabled":true}'
```

## Disable shuffle

```bash
curl -X POST http://localhost:8000/api/rooms/$ROOM_ID/shuffle \
  -H "Authorization: Bearer 124" \
  -H "Content-Type: application/json" \
  -d '{"enabled":false}'
```

---

# 6. Repeat

Supported repeat modes:

```text
none
once
all
```

## No repeat

```bash
curl -X POST http://localhost:8000/api/rooms/$ROOM_ID/repeat \
  -H "Authorization: Bearer 124" \
  -H "Content-Type: application/json" \
  -d '{"mode":"none"}'
```

## Repeat once

```bash
curl -X POST http://localhost:8000/api/rooms/$ROOM_ID/repeat \
  -H "Authorization: Bearer 124" \
  -H "Content-Type: application/json" \
  -d '{"mode":"once"}'
```

## Repeat all

```bash
curl -X POST http://localhost:8000/api/rooms/$ROOM_ID/repeat \
  -H "Authorization: Bearer 124" \
  -H "Content-Type: application/json" \
  -d '{"mode":"all"}'
```

---

# 7. Playback order

## Ascending

```bash
curl -X POST http://localhost:8000/api/rooms/$ROOM_ID/order/ascending \
  -H "Authorization: Bearer 124"
```

## Descending

```bash
curl -X POST http://localhost:8000/api/rooms/$ROOM_ID/order/descending \
  -H "Authorization: Bearer 124"
```

---

# 8. Seek

## Seek forward

Moves the playback position forward by the specified number of seconds.

```bash
curl -X POST http://localhost:8000/api/rooms/$ROOM_ID/seek/front \
  -H "Authorization: Bearer 124" \
  -H "Content-Type: application/json" \
  -d '{"seconds":10}'
```

## Seek backward

Moves the playback position backward by the specified number of seconds.

```bash
curl -X POST http://localhost:8000/api/rooms/$ROOM_ID/seek/back \
  -H "Authorization: Bearer 124" \
  -H "Content-Type: application/json" \
  -d '{"seconds":5}'
```

---

# 9. Audio Quality

Supported values:

```text
low
medium
high
highest
peak
```
 
## Low quality | 48 kbps

```bash
curl -X POST http://localhost:8000/api/rooms/$ROOM_ID/quality \
  -H "Authorization: Bearer 124" \
  -H "Content-Type: application/json" \
  -d '{"quality":"low"}'
```

## Medium quality | 96 kbps

```bash
curl -X POST http://localhost:8000/api/rooms/$ROOM_ID/quality \
  -H "Authorization: Bearer 124" \
  -H "Content-Type: application/json" \
  -d '{"quality":"medium"}'
```

## High quality | 128 kbps

```bash
curl -X POST http://localhost:8000/api/rooms/$ROOM_ID/quality \
  -H "Authorization: Bearer 124" \
  -H "Content-Type: application/json" \
  -d '{"quality":"high"}'
```


## Highest quality | 256 kbps

```bash
curl -X POST http://localhost:8000/api/rooms/$ROOM_ID/quality \
  -H "Authorization: Bearer 124" \
  -H "Content-Type: application/json" \
  -d '{"quality":"highest"}'
```


## Peak quality | 320 kbps

```bash
curl -X POST http://localhost:8000/api/rooms/$ROOM_ID/quality \
  -H "Authorization: Bearer 124" \
  -H "Content-Type: application/json" \
  -d '{"quality":"peak"}'
```

---

# 10. WebRTC

The WebRTC signaling endpoint is used by the browser/client to establish a WebRTC audio connection.

## WebRTC offer

```text
POST /api/rooms/{room_id}/webrtc/offer
```

The request body contains the SDP offer generated by an actual WebRTC peer:

```json
{
  "type": "offer",
  "sdp": "v=0\r\n..."
}
```

The browser should normally make this request automatically through `audio.js`.

A manually constructed `curl` request is not generally useful because the SDP must come from an actual `RTCPeerConnection`.

Open the room in the browser instead:

```text
http://localhost:8000/room/$ROOM_ID
```

---

# 11. Static Web Interface

## Main page

```text
http://localhost:8000/
```

## Room page

```text
http://localhost:8000/room/$ROOM_ID
```

Example:

```text
http://localhost:8000/room/bdf36a19a0a9
```

---

# 12. Complete Test Sequence

The following sequence is useful for testing the full room lifecycle.

## Step 1 — Create a room

```bash
curl -X POST http://localhost:8000/api/rooms \
  -H "Authorization: Bearer 124" \
  -H "Content-Type: application/json" \
  -d '{"name":"Test Room"}'
```

Set the returned room ID:

```bash
ROOM_ID="YOUR_ROOM_ID"
```

## Step 2 — Read the room

```bash
curl http://localhost:8000/api/rooms/$ROOM_ID
```

## Step 3 — Read the queue

```bash
curl http://localhost:8000/api/rooms/$ROOM_ID/queue
```

## Step 4 — Add audio

```bash
curl -X POST http://localhost:8000/api/rooms/$ROOM_ID/queue/add \
  -H "Authorization: Bearer 124" \
  -H "Content-Type: application/json" \
  -d '{
    "title":"Test Audio",
    "path":"/home/bakachii/stuffs/codes/python/pyLiveMusic/audio.mp3"
  }'
```

## Step 5 — Check room state again

```bash
curl http://localhost:8000/api/rooms/$ROOM_ID
```

## Step 6 — Pause

```bash
curl -X POST http://localhost:8000/api/rooms/$ROOM_ID/pause \
  -H "Authorization: Bearer 124"
```

## Step 7 — Resume

```bash
curl -X POST http://localhost:8000/api/rooms/$ROOM_ID/resume \
  -H "Authorization: Bearer 124"
```

## Step 8 — Change volume

```bash
curl -X POST http://localhost:8000/api/rooms/$ROOM_ID/volume \
  -H "Authorization: Bearer 124" \
  -H "Content-Type: application/json" \
  -d '{"volume":0.5}'
```

## Step 9 — Enable shuffle

```bash
curl -X POST http://localhost:8000/api/rooms/$ROOM_ID/shuffle \
  -H "Authorization: Bearer 124" \
  -H "Content-Type: application/json" \
  -d '{"enabled":true}'
```

## Step 10 — Repeat all

```bash
curl -X POST http://localhost:8000/api/rooms/$ROOM_ID/repeat \
  -H "Authorization: Bearer 124" \
  -H "Content-Type: application/json" \
  -d '{"mode":"all"}'
```

## Step 11 — Set quality

```bash
curl -X POST http://localhost:8000/api/rooms/$ROOM_ID/quality \
  -H "Authorization: Bearer 124" \
  -H "Content-Type: application/json" \
  -d '{"quality":"high"}'
```

## Step 12 — Seek forward

```bash
curl -X POST http://localhost:8000/api/rooms/$ROOM_ID/seek/front \
  -H "Authorization: Bearer 124" \
  -H "Content-Type: application/json" \
  -d '{"seconds":10}'
```

## Step 13 — Seek backward

```bash
curl -X POST http://localhost:8000/api/rooms/$ROOM_ID/seek/back \
  -H "Authorization: Bearer 124" \
  -H "Content-Type: application/json" \
  -d '{"seconds":5}'
```

## Step 14 — Skip

```bash
curl -X POST http://localhost:8000/api/rooms/$ROOM_ID/skip \
  -H "Authorization: Bearer 124"
```

## Step 15 — Clear the queue

```bash
curl -X POST http://localhost:8000/api/rooms/$ROOM_ID/queue/clear \
  -H "Authorization: Bearer 124"
```

## Step 16 — End the room

```bash
curl -X POST http://localhost:8000/api/rooms/$ROOM_ID/end \
  -H "Authorization: Bearer 124"
```

---

# 13. Endpoint Summary

| Method | Endpoint | Auth |
|---|---|---|
| `POST` | `/api/rooms` | Yes |
| `GET` | `/api/rooms/{room_id}` | No |
| `POST` | `/api/rooms/{room_id}/end` | Yes |
| `GET` | `/api/rooms/{room_id}/queue` | No |
| `POST` | `/api/rooms/{room_id}/queue/add` | Yes |
| `POST` | `/api/rooms/{room_id}/queue/{track_id}/remove` | Yes |
| `POST` | `/api/rooms/{room_id}/queue/clear` | Yes |
| `POST` | `/api/rooms/{room_id}/pause` | Yes |
| `POST` | `/api/rooms/{room_id}/resume` | Yes |
| `POST` | `/api/rooms/{room_id}/skip` | Yes |
| `POST` | `/api/rooms/{room_id}/volume` | Yes |
| `POST` | `/api/rooms/{room_id}/shuffle` | Yes |
| `POST` | `/api/rooms/{room_id}/repeat` | Yes |
| `POST` | `/api/rooms/{room_id}/order/ascending` | Yes |
| `POST` | `/api/rooms/{room_id}/order/descending` | Yes |
| `POST` | `/api/rooms/{room_id}/seek/front` | Yes |
| `POST` | `/api/rooms/{room_id}/seek/back` | Yes |
| `POST` | `/api/rooms/{room_id}/quality` | Yes |
| `POST` | `/api/rooms/{room_id}/webrtc/offer` | No* |

\* WebRTC signaling is normally called by the browser/client rather than manually through `curl`.

---