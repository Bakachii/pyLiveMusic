import uuid
import random
import asyncio
from dataclasses import dataclass

from aiortc import RTCSessionDescription
from aiortc.contrib.media import MediaRelay

from pyLiveMusic._logger import logs
from _utils._settings import (
    DB_TIMEOUT,
    MAX_QUEUE_LENGTH,
    MAX_ROOMS,
    ROOM_DELETE_DELAY,
    ServerOptions,
)

from .peer import Peer
from .audio import RoomAudioTrack


class RoomExistsError(ValueError):
    pass


@dataclass
class QueueItem:
    id: str
    title: str
    path: str


class Room:
    def __init__(
        self,
        room_id,
        name,
        controllers,
        on_empty,
        options=None,
    ):
        self.options = options or ServerOptions()
        self.id = room_id
        self.name = name

        self.controllers = set(controllers)
        self.on_empty = on_empty

        # Queue

        self.queue = []
        self.current = None
        self._repeat_current = False

        # Playback

        self.playing = False
        self.started = False
        self.volume = 1.0
        self.quality = "high"
        self.shuffle = False
        self.repeat_mode = "none"
        self.order = "ascending"

        # WebRTC

        self.relay = MediaRelay()
        self.audio = RoomAudioTrack(
            self._track_finished
        )
        self.peers = set()

        # Lifecycle

        self.delete_task = None
        self.ended = False
        self.lock = asyncio.Lock()

    # Queue

    async def add_track(self, title, path):
        async with self.lock:
            if len(self.queue) >= MAX_QUEUE_LENGTH:
                raise ValueError("QUEUE_FULL")

            item = QueueItem(
                id=uuid.uuid4().hex,
                title=title,
                path=path,
            )

            self.queue.append(item)
            self.cancel_delete_timer()

            if self.current is None:
                dropped = await self._start_next_locked()

                # The file could not be opened: say so instead of leaving a
                # room that looks alive but never plays.
                if item in dropped:
                    raise ValueError("TRACK_UNPLAYABLE")

            return item

    # Start next track

    async def _start_next_locked(self, start=None):
        """Loads the next playable track.

        A track that cannot be opened is dropped (and logged) and the next
        one is tried, so one bad file never leaves the room stuck. Returns
        the dropped items.
        """
        dropped = []

        while True:
            if self.ended:
                return dropped

            if not self.queue:
                self.current = None
                self.playing = False

                await self.audio.pause()
                self.schedule_delete()

                return dropped

            if self.shuffle:
                index = random.randrange(
                    len(self.queue)
                )

            elif self.order == "ascending":
                index = 0

            else:
                index = len(self.queue) - 1

            item = self.queue.pop(index)

            try:
                await self.audio.load(item.path)

            except Exception as error:
                logs.error(
                    f"[ROOM] {self.id}: cannot play "
                    f"{item.path!r}: {error}"
                )

                dropped.append(item)
                continue

            self.current = item

            self.audio.set_volume(
                self.volume
            )

            if start is None:
                start = self.started

            if start:
                await self.audio.play()
                self.playing = True

            else:
                self.playing = False

            return dropped

    # Track finished

    async def _track_finished(self):
        async with self.lock:
            if self.current is None:
                return

            finished = self.current

            # Repeat once

            if self.repeat_mode == "once":
                self.repeat_mode = "none"

                try:
                    await self.audio.load(
                        finished.path
                    )

                    self.audio.set_volume(
                        self.volume
                    )

                    await self.audio.play()

                    self.playing = True
                    self.started = True

                    return

                except Exception as error:
                    logs.error(
                        f"[ROOM] {self.id}: cannot repeat "
                        f"{finished.path!r}: {error}"
                    )

            # Repeat all

            if self.repeat_mode == "all":
                self.queue.append(
                    finished
                )

            self.current = None

            await self._start_next_locked(
                start=True
            )

    # Pause

    async def pause(self):
        async with self.lock:
            if self.current is None:
                raise ValueError(
                    "NOT_PLAYING_ANYTHING_CURRENTLY"
                )

            await self.audio.pause()

            self.playing = False

    # Resume

    async def resume(self):
        async with self.lock:
            if self.current is None:
                raise ValueError(
                    "NOT_PLAYING_ANYTHING_CURRENTLY"
                )

            await self.audio.play()

            self.playing = True
            self.started = True

    # Skip

    async def skip(self):
        async with self.lock:
            if self.current is None:
                raise ValueError(
                    "NOT_PLAYING_ANYTHING_CURRENTLY"
                )

            was_playing = self.playing

            self.current = None

            await self.audio.pause()

            await self._start_next_locked(
                start=was_playing
            )

    # Seek

    async def seek_front(self, seconds):
        async with self.lock:
            self._validate_seek(seconds)

            position = (
                self.audio.current_position()
                + seconds
            )

            await self.audio.seek(position)

    async def seek_back(self, seconds):
        async with self.lock:
            self._validate_seek(seconds)

            position = (
                self.audio.current_position()
                - seconds
            )

            await self.audio.seek(position)

    def _validate_seek(self, seconds):
        if self.current is None:
            raise ValueError(
                "NOT_PLAYING_ANYTHING_CURRENTLY"
            )

        try:
            seconds = float(seconds)

        except (TypeError, ValueError):
            raise ValueError(
                "INVALID_SEEK_SECONDS"
            )

        if seconds < 0:
            raise ValueError(
                "INVALID_SEEK_SECONDS"
            )

        duration = self.audio.duration
        current = self.audio.current_position()

        if (
            seconds > duration
            or current + seconds > duration
            or current - seconds < 0
        ):
            raise ValueError(
                "INVALID_SEEK_LIMIT"
            )

    # Volume

    async def set_volume(self, volume):
        async with self.lock:
            try:
                volume = float(volume)

            except (TypeError, ValueError):
                raise ValueError(
                    "INVALID_VOLUME"
                )

            if not 0 <= volume <= 1:
                raise ValueError(
                    "INVALID_VOLUME"
                )

            self.volume = volume
            self.audio.set_volume(volume)

    # Shuffle

    async def set_shuffle(self, enabled):
        self.shuffle = bool(enabled)

    # Repeat

    async def set_repeat(self, mode):
        if mode not in {
            "none",
            "once",
            "all",
        }:
            raise ValueError(
                "INVALID_REPEAT_MODE"
            )

        self.repeat_mode = mode

    # Order

    async def set_order(self, order):
        if order not in {
            "ascending",
            "descending",
        }:
            raise ValueError(
                "INVALID_PLAY_ORDER"
            )

        self.order = order

    # Quality

    async def set_quality(self, quality):
        if quality not in {
            "low",
            "medium",
            "high",
            "highest",
            "peak",
        }:
            raise ValueError(
                "INVALID_AUDIO_QUALITY"
            )

        self.quality = quality

        for peer in self.peers:
            try:
                await peer.set_quality(
                    quality
                )

            except Exception:
                pass

    # WebRTC peer

    async def add_peer(self, peer_id=None, remote=None):
        limit = self.options.max_peers_per_room

        if limit and len(self.peers) >= limit:
            raise ValueError("ROOM_FULL")

        peer = Peer(
            self.relay,
            self.audio,
            self.quality,
            on_close=self.remove_peer,
            on_ready=self._peer_ready,
            options=self.options,
        )

        peer.remote = remote

        peer.id = (
            peer_id
            or uuid.uuid4().hex
        )

        self.peers.add(peer)

        return peer

    def get_peer(self, peer_id):
        for peer in self.peers:
            if peer.id == peer_id:
                return peer

        return None

    async def remove_peer(self, peer):
        self.peers.discard(peer)

        await peer.close()

    # WebRTC offer

    async def offer(self, peer, sdp):
        offer = RTCSessionDescription(
            sdp=sdp,
            type="offer",
        )

        await peer.connection.setRemoteDescription(
            offer
        )

        await peer.set_remote_ready()

        answer = await peer.connection.createAnswer()

        await peer.connection.setLocalDescription(
            answer
        )

        return peer.connection.localDescription

    # State

    def state(self):
        return {
            "room_id": self.id,
            "name": self.name,
            "participants": len(
                self.peers
            ),
            "playing": self.playing,

            "position": (
                self.audio.current_position()
                if self.current is not None
                else 0.0
            ),

            "duration": (
                self.audio.duration
                if self.current is not None
                else 0.0
            ),

            "volume": self.volume,
            "quality": self.quality,
            "shuffle": self.shuffle,
            "repeat": self.repeat_mode,
            "order": self.order,

            "current": (
                {
                    "id": self.current.id,
                    "title": self.current.title,
                }
                if self.current is not None
                else None
            ),

            "queue": [
                {
                    "id": item.id,
                    "title": item.title,
                }
                for item in self.queue
            ],
        }

    # Start playback after first peer connects

    async def _peer_ready(self, peer):
        async with self.lock:
            if self.started:
                return

            if self.current is None:
                return

            await self.audio.play()

            self.playing = True
            self.started = True

            logs.info(
                f"[ROOM] First peer ready: "
                f"{peer.id} - playback started"
            )

    # State including stopped room

    def state_or_not_playing(self):
        if self.current is None:
            return {
                "code":
                    "NOT_PLAYING_ANYTHING_CURRENTLY",

                "room_id":
                    self.id,

                "queue_length":
                    len(self.queue),
            }

        return self.state()

    # Empty queue timer

    def schedule_delete(self):
        self.cancel_delete_timer()

        self.delete_task = asyncio.create_task(
            self._delete_after_delay()
        )

    def cancel_delete_timer(self):
        task, self.delete_task = self.delete_task, None

        # end() runs inside this very task when the timer fires. Cancelling
        # ourselves would abort the clean-up half way (peers left open, audio
        # never closed, database record never deleted).
        if task is not None and task is not asyncio.current_task():
            task.cancel()

    async def _delete_after_delay(self):
        try:
            await asyncio.sleep(
                ROOM_DELETE_DELAY
            )

        except asyncio.CancelledError:
            return

        if self.queue or self.current is not None or self.ended:
            return

        try:
            await self.on_empty(
                self.id
            )

        except Exception:
            logs.exception(
                f"[ROOM] {self.id}: automatic delete failed"
            )

    # End room

    async def end(self):
        if self.ended:
            return

        self.ended = True
        self.cancel_delete_timer()

        peers = list(self.peers)
        self.peers.clear()

        try:
            if peers:
                await asyncio.gather(
                    *(
                        asyncio.wait_for(peer.close(), 5)
                        for peer in peers
                    ),
                    return_exceptions=True,
                )

        finally:
            try:
                await self.audio.close()

            except Exception:
                logs.exception(
                    f"[ROOM] {self.id}: closing audio failed"
                )


class RoomManager:
    def __init__(self, repository):
        self.rooms = {}
        self.repository = repository

        # Set by the server before it starts.
        self.options = ServerOptions()
        self.owner_id = None

    def total_peers(self):
        return sum(len(room.peers) for room in self.rooms.values())

    def peers_from(self, remote):
        return sum(
            1
            for room in self.rooms.values()
            for peer in room.peers
            if getattr(peer, "remote", None) == remote
        )

    async def _db(self, coroutine, what):
        """Database calls are best effort: live rooms never wait for, or
        fail because of, a slow or unreachable database."""
        try:
            return await asyncio.wait_for(
                coroutine,
                DB_TIMEOUT,
            )

        except Exception as error:
            logs.warning(f"[DB] {what} failed: {error!r}")

    async def start(self):
        documents = await self.repository.list()

        for document in documents:
            room_id = document["_id"]

            if room_id in self.rooms:
                continue

            controllers = document.get(
                "controllers",
                [],
            )

            # Older versions stored the API key itself here. Keep only the
            # non-secret owner id.
            if self.owner_id and controllers != [self.owner_id]:
                controllers = [self.owner_id]

                await self._db(
                    self.repository.create(
                        room_id=room_id,
                        name=document.get("name", "Private Room"),
                        controllers=controllers,
                    ),
                    "scrub room",
                )

            room = Room(
                room_id,
                document.get(
                    "name",
                    "Private Room",
                ),
                controllers,
                self.remove,
                self.options,
            )

            self.rooms[room_id] = room

            # Queues are not persisted, so a revived room is empty. Let it
            # expire like any other idle room instead of living forever.
            room.schedule_delete()

        logs.info(
            "Room manager started"
        )

    async def shutdown(self):
        for room in list(
            self.rooms.values()
        ):
            try:
                await room.end()

            except Exception:
                logs.exception("Room shutdown failed")

        self.rooms.clear()

    async def create(
        self,
        name,
        controllers,
        room_id=None,
    ):
        if room_id is None:
            room_id = uuid.uuid4().hex[:12]

        if room_id in self.rooms:
            raise RoomExistsError(
                "ROOM_EXISTS"
            )

        if len(self.rooms) >= MAX_ROOMS:
            raise ValueError("TOO_MANY_ROOMS")

        room = Room(
            room_id,
            name,
            controllers,
            self.remove,
            self.options,
        )

        self.rooms[room_id] = room

        await self._db(
            self.repository.create(
                room_id=room_id,
                name=name,
                controllers=controllers,
            ),
            "save room",
        )

        return room

    def get(self, room_id):
        return self.rooms.get(room_id)

    async def remove(self, room_id):
        room = self.rooms.pop(
            room_id,
            None,
        )

        try:
            if room:
                await room.end()

        finally:
            await self._db(
                self.repository.delete(
                    room_id
                ),
                "delete room",
            )
