import asyncio

from aiortc import RTCPeerConnection
from aiortc.contrib.media import MediaRelay

from pyLiveMusic._logger import logs
from _utils._settings import QUALITY_BITRATES


class Peer:
    def __init__(
        self,
        relay,
        audio_track,
        quality="high",
        on_close=None,
        on_ready=None,
    ):
        self.id = None
        self.connection = RTCPeerConnection()
        logs.info("[WEBRTC] Creating peer")

        self.audio = relay.subscribe(audio_track)
        logs.info("[WEBRTC] Subscribed to audio")

        self.sender = self.connection.addTrack(self.audio)
        logs.info("[WEBRTC] Audio track added")

        self.quality = quality
        self._on_close = on_close
        self._on_ready = on_ready
        self._closed = False
        self._ready = False

        self._remote_ready = asyncio.Event()
        self._pending_candidates = []

        @self.connection.on("connectionstatechange")
        async def connection_state():
            state = self.connection.connectionState

            logs.info(
                f"[WEBRTC] Connection state: {state}"
            )

            if state == "connected":
                if not self._ready:
                    self._ready = True

                    if self._on_ready:
                        await self._on_ready(self)

            elif state in ("closed", "failed"):
                if self._on_close and not self._closed:
                    self._closed = True
                    await self._on_close(self)

        @self.connection.on("iceconnectionstatechange")
        async def ice_state():
            logs.info(
                f"[WEBRTC] ICE state: "
                f"{self.connection.iceConnectionState}"
            )

        @self.connection.on("signalingstatechange")
        async def signaling_state():
            logs.info(
                f"[WEBRTC] Signaling state: "
                f"{self.connection.signalingState}"
            )

    async def add_candidate(self, candidate):
        if not self._remote_ready.is_set():
            self._pending_candidates.append(candidate)
            return

        await self.connection.addIceCandidate(candidate)

    async def set_remote_ready(self):
        self._remote_ready.set()

        for candidate in self._pending_candidates:
            await self.connection.addIceCandidate(candidate)

        self._pending_candidates.clear()

    async def set_quality(self, quality):
        if quality not in QUALITY_BITRATES:
            raise ValueError("INVALID_AUDIO_QUALITY")

        self.quality = quality

        parameters = self.sender.getParameters()
        bitrate = QUALITY_BITRATES[quality]

        for encoding in parameters.encodings:
            encoding.maxBitrate = bitrate

        await self.sender.setParameters(parameters)

    async def close(self):
        if self._closed:
            return

        self._closed = True
        await self.connection.close()