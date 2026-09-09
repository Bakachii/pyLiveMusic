## Quick Start

```python
import asyncio

from pyLiveMusic import Client
from pyLiveMusic.player import Room, Queue, Playback


async def main():
    client = Client(player_function=True)

    try:
        await client.start()

        room = client.get(Room)
        queue = client.get(Queue)
        playback = client.get(Playback)

        data = await room.create(name="Lo-fi")
        room_id = data["room_id"]

        await queue.add_track(
            room_id=room_id,
            title="Audio Title",
            path="/path/to/audio.mp3",
        )

        await playback.resume(room_id)

        await client.run_until_disconnect()

    finally:
        await client.stop()


asyncio.run(main())
```

`player_function=True` enables the player API. `client.get(...)` returns the already-initialized player instance.

<details>
<summary><strong>Room</strong></summary>

Handles room lifecycle.

| Function | Arguments | Description |
|---|---|---|
| `create()` | `name="Private Room"`, `room_id=None` | Creates a room and returns its data. An optional `room_id` lets you choose the ID. |
| `get()` | `room_id` | Retrieves a room by ID. |
| `end()` | `room_id` | Ends a room and returns the server response. |
| `get_embed()` | `room_id` | Returns a ready-to-use iframe embed snippet. |

```python
room = client.get(Room)

data = await room.create(name="Lo-fi")
room_id = data["room_id"]

room_data = await room.get(room_id)
ended = await room.end(room_id)
```

</details>

<details>
<summary><strong>Queue</strong></summary>

Manages tracks associated with a room.

| Function | Arguments | Description |
|---|---|---|
| `get_queue()` | `room_id` | Gets the current track and queued tracks. |
| `add_track()` | `room_id`, `title`, `path` | Adds an audio file to the queue and returns its ID and title. |
| `remove_track()` | `room_id`, `track_id` | Removes a queued track by ID. |
| `clear_queue()` | `room_id` | Clears all queued tracks. |

```python
queue = client.get(Queue)

track = await queue.add_track(
    room_id=room_id,
    title="Audio Title",
    path="/path/to/audio.mp3",
)

data = await queue.get_queue(room_id)

await queue.remove_track(
    room_id=room_id,
    track_id=track["id"],
)

await queue.clear_queue(room_id)
```

A track added while nothing is playing may start playing immediately instead of remaining only in the queue.

</details>

<details>
<summary><strong>Playback</strong></summary>

Controls playback and room audio state.

| Function | Arguments | Description |
|---|---|---|
| `pause()` | `room_id` | Pauses the current track. |
| `resume()` | `room_id` | Resumes playback. |
| `skip()` | `room_id` | Skips the current track. |
| `volume()` | `room_id`, `volume` | Sets volume from `0.0` to `1.0`. |
| `mute()` | `room_id` | Mutes playback by setting volume to `0`. |
| `shuffle()` | `room_id`, `enabled` | Enables or disables shuffle. |
| `repeat()` | `room_id`, `mode="once"` | Sets the repeat mode. |
| `order()` | `room_id`, `direction="ascending"` | Sets playback order. |
| `seek()` | `room_id`, `seconds`, `direction="front"` | Moves playback forward or backward. |
| `quality()` | `room_id`, `quality` | Sets audio quality. |

<details>
<summary><strong>repeat() options</strong></summary>

Supported modes:

```text
none
once
all
```

```python
await playback.repeat(room_id, "none")
await playback.repeat(room_id, "once")
await playback.repeat(room_id, "all")
```

</details>

<details>
<summary><strong>order() options</strong></summary>

Supported directions:

```text
ascending
descending
```

```python
await playback.order(room_id, "ascending")
await playback.order(room_id, "descending")
```

</details>

<details>
<summary><strong>seek() options</strong></summary>

`direction` accepts:

```text
front
back
```

```python
await playback.seek(
    room_id=room_id,
    seconds=10,
    direction="front",
)

await playback.seek(
    room_id=room_id,
    seconds=5,
    direction="back",
)
```

</details>

<details>
<summary><strong>quality() options</strong></summary>

Supported quality levels:

| Value | Bitrate |
|---|---:|
| `low` | 48 kbps |
| `medium` | 96 kbps |
| `high` | 128 kbps |
| `highest` | 256 kbps |
| `peak` | 320 kbps |

```python
await playback.quality(room_id, "high")
```

</details>

```python
playback = client.get(Playback)

await playback.pause(room_id)
await playback.resume(room_id)
await playback.skip(room_id)

await playback.volume(room_id, 0.75)
await playback.mute(room_id)

await playback.shuffle(room_id, True)
await playback.repeat(room_id, "all")
await playback.order(room_id, "ascending")

await playback.seek(room_id, 10, "front")
await playback.quality(room_id, "high")
```

</details>

## Client Lifecycle

```python
client = Client(player_function=True)

room = client.get(Room)
queue = client.get(Queue)
playback = client.get(Playback)
```

`client.get()` retrieves the existing initialized instance; it does not create another player object.

Multiple player instances can be retrieved together:

```python
room, queue, playback = client.get(
    Room,
    Queue,
    Playback,
)
```

## Notes

- All player methods are asynchronous.
- Use the `room_id` returned by `Room.create()` for room-specific operations.
- Queue removal targets queued items; it is not intended to remove the currently playing track.
- `volume` uses a `0.0`–`1.0` range, where `0` is muted and `1.0` is full volume.