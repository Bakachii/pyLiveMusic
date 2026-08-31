import uuid
import random
import asyncio
from dataclasses import dataclass

from aiortc import RTCSessionDescription
from aiortc.contrib.media import MediaRelay

from pyLiveMusic._utils._settings import ROOM_DELETE_DELAY

from .peer import Peer
from .audio import RoomAudioTrack


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
    ):

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
        self.volume = 1.0
        self.quality = "high"
        self.shuffle = False
        self.repeat_mode = "none"
        self.order = "ascending"


        # WebRTC

        self.relay = MediaRelay()
        self.audio = RoomAudioTrack(self._track_finished)
        self.peers = set()


        # Lifecycle

        self.delete_task = None
        self.ended = False
        self.lock = asyncio.Lock()


    # Queue

    async def add_track(self, title, path):

        async with self.lock:
            item = QueueItem(
                id=uuid.uuid4().hex,
                title=title,
                path=path,
            )

            self.queue.append(item)
            self.cancel_delete_timer()

            if self.current is None:
                await self._start_next_locked()

            return item


    # Start next track

    async def _start_next_locked(self):
        if self.ended:
            return


        # No tracks

        if not self.queue:
            self.current = None
            self.playing = False

            await self.audio.pause()
            self.schedule_delete()

            return


        # Select next

        if self.shuffle:
            index = random.randrange(len(self.queue))

        elif self.order == "ascending":
            index = 0

        else:
            index = len(self.queue) - 1

        item = self.queue.pop(index)

        self.current = item

        await self.audio.load(item.path)

        self.audio.set_volume(self.volume)
        self.playing = True

        await self.audio.play()


    # Track finished

    async def _track_finished(self):
        async with self.lock:

            if self.current is None:
                return

            finished = self.current


            # Repeat once

            if self.repeat_mode == "once":
                self.repeat_mode = "none"

                await self.audio.load(finished.path)
                
                self.audio.set_volume(self.volume)
                self.playing = True

                await self.audio.play()

                return


            # Repeat all

            if self.repeat_mode == "all":
                self.queue.append(finished)

            self.current = None
            await self._start_next_locked()


    # Pause

    async def pause(self):
        async with self.lock:
            if self.current is None:
                raise ValueError("NOT_PLAYING_ANYTHING_CURRENTLY")

            await self.audio.pause()
            self.playing = False


    # Resume

    async def resume(self):
        async with self.lock:
            if self.current is None:
                raise ValueError("NOT_PLAYING_ANYTHING_CURRENTLY")

            await self.audio.play()
            self.playing = True


    # Skip

    async def skip(self):
        async with self.lock:
            if self.current is None:
                raise ValueError("NOT_PLAYING_ANYTHING_CURRENTLY")

            self.current = None

            await self.audio.pause()
            await self._start_next_locked()


    # Seek

    async def seek_front(self, seconds):
        
        async with self.lock:
            self._validate_seek(seconds)
            position = self.audio.current_position() + seconds

            await self.audio.seek(position)

    async def seek_back(self, seconds):

        async with self.lock:
            self._validate_seek(seconds)

            position = self.audio.current_position() - seconds

            await self.audio.seek(position)

    def _validate_seek(self, seconds):

        if self.current is None:
            raise ValueError("NOT_PLAYING_ANYTHING_CURRENTLY")

        try:
            seconds = float(seconds)

        except (TypeError, ValueError):
            raise ValueError("INVALID_SEEK_SECONDS")

        if seconds < 0:
            raise ValueError("INVALID_SEEK_SECONDS")

        duration = self.audio.duration
        current = self.audio.current_position()

        if (
            seconds > duration
            or current + seconds > duration
            or current - seconds < 0
        ):

            raise ValueError("INVALID_SEEK_LIMIT")


    # Volume

    async def set_volume(self, volume):

        async with self.lock:
            try:
                volume = float(volume)

            except (TypeError, ValueError):
                raise ValueError("INVALID_VOLUME")

            if not 0 <= volume <= 1:
                raise ValueError("INVALID_VOLUME")

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

            raise ValueError("INVALID_REPEAT_MODE")

        self.repeat_mode = mode


    # Order

    async def set_order(self, order):

        if order not in {
            "ascending",
            "descending",
        }:

            raise ValueError("INVALID_PLAY_ORDER")

        self.order = order


    # Quality

    async def set_quality(self, quality):

        if quality not in {
            "low",
            "medium",
            "high",
        }:

            raise ValueError("INVALID_AUDIO_QUALITY")

        self.quality = quality

        for peer in self.peers:
            try:
                await peer.set_quality(quality)

            except Exception:
                pass


    # WebRTC peer

    async def add_peer(self):
        peer = Peer(
            self.relay,
            self.audio,
            self.quality,
        )
        self.peers.add(peer)

        return peer

    async def remove_peer(self, peer):
        self.peers.discard(peer)

        await peer.close()


    # WebRTC offer

    async def offer(self, peer, sdp):

        offer = RTCSessionDescription(sdp=sdp, type="offer")
        await peer.connection.setRemoteDescription(offer)
        
        answer = await peer.connection.createAnswer()
        await peer.connection.setLocalDescription(answer)

        return peer.connection.localDescription


    # State

    def state(self):

        return {
            "room_id": self.id,
            "name": self.name,

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
        self.delete_task = asyncio.create_task(self._delete_after_delay())

    def cancel_delete_timer(self):
        if self.delete_task:
            self.delete_task.cancel()
            self.delete_task = None

    async def _delete_after_delay(self):
        try:
            await asyncio.sleep(ROOM_DELETE_DELAY)

        except asyncio.CancelledError:
            return

        if self.queue:
            return

        await self.on_empty(self.id)


    # End room

    async def end(self):
        if self.ended:
            return

        self.ended = True
        self.cancel_delete_timer()

        for peer in list(self.peers):
            await peer.close()

        self.peers.clear()
        await self.audio.close()

class RoomManager:

    def __init__(self, repository):
        self.rooms = {}
        self.repository = repository

    async def start(self):
        print("Room manager started")

    async def shutdown(self):
        for room in list(self.rooms.values()):
            await room.end()

        self.rooms.clear()

    async def create(self, name, controllers):
        room_id = uuid.uuid4().hex[:12]

        room = Room(
            room_id,
            name,
            controllers,
            self.remove,
        )

        self.rooms[room_id] = room

        await self.repository.create(
            room_id=room_id,
            name=name,
            controllers=controllers,
        )

        return room

    def get(self, room_id):
        return self.rooms.get(room_id)

    async def remove(self, room_id):
        room = self.rooms.pop(room_id, None)

        if room:
            await room.end()

        await self.repository.delete(room_id)