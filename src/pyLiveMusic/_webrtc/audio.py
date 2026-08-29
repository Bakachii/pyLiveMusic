import av
import time
import asyncio
import numpy as np
from pathlib import Path
from collections import deque
from fractions import Fraction

from aiortc import MediaStreamTrack

from pyLiveMusic._settings import  SAMPLE_RATE, FRAME_SAMPLES


TIME_BASE = Fraction(1, SAMPLE_RATE)


class RoomAudioTrack(MediaStreamTrack):

    kind = "audio"

    def __init__(self, on_track_finished):
        super().__init__()

        self.on_track_finished = on_track_finished

        # Decoder

        self.container = None
        self.stream = None
        self.decoder = None
        self.resampler = None

        self.filename = None


        # Playback
       
        self.duration = 0.0
        self.position = 0.0

        self.paused = True

        self.volume = 1.0


        # Audio timing

        self._timestamp = 0
        self._start_time = None

        # Resampled frames waiting to be sent.
        self._pending_frames = deque()
        self._finished = False


        # Synchronization

        self._condition = asyncio.Condition()
        self._generation = 0
        self._finish_task = None


    # Load a new audio file

    async def load(self, filename: str, position: float = 0.0):

        filename = str(Path(filename).resolve())
        await self.close_file()
        print(f"[AUDIO] Loading: {filename}")

        self.container = av.open(filename)
        self.stream = (self.container.streams.audio[0])

        self.decoder = (self.container.decode(self.stream))
        self.resampler = av.AudioResampler(
            format="s16",
            layout="stereo",
            rate=SAMPLE_RATE,
            frame_size=FRAME_SAMPLES,
        )

        self.filename = filename
        self.duration = self._get_duration()

        self.position = max(0.0, min(float(position), self.duration))

        # Clear any frames belonging the previous audio.
        
        self._pending_frames.clear()
        self._timestamp = int(self.position * SAMPLE_RATE)

        self._start_time = time.monotonic() - self.position
        self._finished = False
        self._generation += 1

        print(
            f"[AUDIO] Duration: "
            f"{self.duration:.3f}s"
        )

        if self.position > 0:
            self._seek_decoder(self.position)


    # Get duration

    def _get_duration(self):

        if (
            self.stream is not None
            and self.stream.duration is not None
            and self.stream.time_base is not None
        ):

            return float(self.stream.duration * self.stream.time_base)

        if (
            self.container is not None
            and self.container.duration is not None
        ):

            return self.container.duration / 1_000_000

        return 0.0


    # Play

    async def play(self):

        async with self._condition:
            if not self.paused:
                return

            self._start_time = time.monotonic() - self.position
            self.paused = False
            self._condition.notify_all()

        print(
            f"[AUDIO] PLAY "
            f"{self.position:.3f}s"
        )

    # Pause

    async def pause(self):
        async with self._condition:
            if self.paused:
                return

            self.position = self.current_position()
            self.paused = True

        print(
            f"[AUDIO] PAUSE "
            f"{self.position:.3f}s"
        )


    # Current playback position

    def current_position(self):
        if self.paused:
            return self.position

        if self._start_time is None:
            return self.position

        position = time.monotonic() - self._start_time

        if self.duration > 0:
            position = min(position, self.duration)

        return max(0.0, position)

    
    # Seek
    
    async def seek(self, position: float):

        if self.duration <= 0:
            raise ValueError("TRACK_DURATION_UNKNOWN")

        if position < 0 or position > self.duration:
            raise ValueError("INVALID_SEEK_LIMIT")

        async with self._condition:

            was_paused = self.paused

            self._seek_decoder(position)
            self._pending_frames.clear()
            self.position = position

            self._timestamp = int(position * SAMPLE_RATE)
            self._start_time = time.monotonic() - position

            self.paused = was_paused
            self._finished = False
            self._condition.notify_all()

        print(
            f"[AUDIO] SEEK "
            f"{position:.3f}s"
        )

    def _seek_decoder(self, position: float):

        if self.container is None or self.stream is None:
            return

        timestamp = int(position / float(self.stream.time_base))

        self.container.seek(
            timestamp,
            stream=self.stream,
            backward=True,
        )

        self.decoder = self.container.decode(self.stream)


    # Volume

    def set_volume(self, volume: float):

        if not 0 <= volume <= 1:
            raise ValueError("INVALID_VOLUME")

        self.volume = float(volume)

    # Decode more audio

    def _decode_next_frame(self):
        while not self._pending_frames:
            try:
                decoded = next(self.decoder)

            except StopIteration:

                # Flush resampler once.
                flushed = (
                    self.resampler.resample(
                        None
                    )
                    if self.resampler
                    else []
                )

                if not isinstance(flushed, list):
                    flushed = [flushed]

                for frame in flushed:
                    if frame.samples > 0:
                        self._pending_frames.append(frame)

                if not self._pending_frames:
                    return False

                break

            frames = self.resampler.resample(decoded)

            if not isinstance(frames, list):
                frames = [frames]

            for frame in frames:
                if frame.samples > 0:
                    self._pending_frames.append(frame)

        return bool(self._pending_frames)


    # Receive WebRTC audio frame

    async def recv(self):

        while True:

            # Pause handling

            async with self._condition:
                while self.paused:
                    await self._condition.wait()

            # Make sure we have audio

            if self.decoder is None:
                await asyncio.sleep(0.01)
                continue

            if not self._pending_frames:
                has_audio = self._decode_next_frame()

                if not has_audio:
                    if not self._finished:
                        self._finished = True

                        print("[AUDIO] TRACK FINISHED")

                        # Don't await the room callback
                        # directly inside recv().
                        #
                        # The callback may replace the
                        # decoder that recv() is currently
                        # using.
                        if (
                            self._finish_task
                            is None
                            or self._finish_task.done()
                        ):

                            self._finish_task = asyncio.create_task(self.on_track_finished())

                    await asyncio.sleep(0.01)
                    continue


            # Take exactly one frame

            frame = self._pending_frames.popleft()


            # Normalize frame format

            frame = self._normalize_frame(frame)

            
            # Timestamp

            timestamp = self._timestamp
            frame.pts = timestamp
            frame.time_base = TIME_BASE
            frame.sample_rate = SAMPLE_RATE


            # Position represented by the
            # beginning of this frame.
            frame_position = timestamp / SAMPLE_RATE


            # Real-time pacing
            # Every 960 samples = 20 ms.

            if self._start_time is None:
                self._start_time = time.monotonic() - frame_position
            
            target_time = self._start_time + frame_position

            delay = target_time - time.monotonic()

            if delay > 0:
                await asyncio.sleep(delay)

            
            # Apply room volume

            if self.volume != 1.0:
                frame = self._apply_volume(frame)
                frame.pts = timestamp
                frame.time_base = TIME_BASE
                frame.sample_rate = SAMPLE_RATE

    
            # Advance clock AFTER returning this frame

            self._timestamp += frame.samples

            self.position = self._timestamp / SAMPLE_RATE

            """print(
                f"[AUDIO] FRAME "
                f"pts={frame.pts} "
                f"samples={frame.samples} "
                f"position={self.position:.3f}"
            )"""

            return frame


    # Normalize audio frame

    def _normalize_frame(self, frame):

        if (
            frame.format.name == "s16"
            and frame.layout.name == "stereo"
            and frame.sample_rate == SAMPLE_RATE
        ):

            return frame

        normalized = (
            av.AudioFrame.from_ndarray(
                frame.to_ndarray(),
                format="s16",
                layout="stereo",
            )
        )

        normalized.sample_rate = SAMPLE_RATE
        
        return normalized


    # Volume

    def _apply_volume(self, frame):

        samples = frame.to_ndarray()
        samples = samples.astype(np.float32) * self.volume
        samples = np.clip(samples, -32768, 32767).astype(np.int16)

        new_frame = (
            av.AudioFrame.from_ndarray(
                samples,
                format="s16",
                layout="stereo",
            )
        )

        new_frame.sample_rate = SAMPLE_RATE

        return new_frame


    # Close

    async def close_file(self):
        self._pending_frames.clear()

        if self.container is not None:
            self.container.close()

        self.container = None
        self.stream = None
        self.decoder = None
        self.resampler = None

    async def close(self):
        await self.close_file()

        if (
            self._finish_task is not None
            and not self._finish_task.done()
        ):

            self._finish_task.cancel()

        self.stop()