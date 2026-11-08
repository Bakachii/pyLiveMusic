import asyncio

from aiortc import RTCConfiguration, RTCIceServer, RTCPeerConnection
from aiortc.contrib.media import MediaRelay

from pyLiveMusic._logger import logs
from _utils._settings import QUALITY_BITRATES, ServerOptions


def server_configuration(options):
    """ICE configuration for the server side of a connection.

    The server normally has a public address, so it only needs STUN (or
    nothing). TURN is for the browsers: see Client(TURN_URLS=...). With no
    ice_servers configured aiortc's default STUN is used, as before.
    """
    if not options.ice_servers:
        return None

    servers = []

    for entry in options.ice_servers:
        urls = entry.get("urls") or []
        urls = [urls] if isinstance(urls, str) else list(urls)
        stun = [url for url in urls if url.startswith(("stun:", "stuns:"))]

        if stun:
            servers.append(RTCIceServer(urls=stun))

    return RTCConfiguration(iceServers=servers)


class Peer:
    def __init__(
        self,
        relay,
        audio_track,
        quality="high",
        on_close=None,
        on_ready=None,
        options=None,
    ):
        options = options or ServerOptions()

        self.id = None
        self.remote = None
        self.candidates_added = 0
        self.connection = RTCPeerConnection(
            configuration=server_configuration(options)
        )
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

        # A peer that never connects (blocked UDP, closed tab, hostile
        # client) would otherwise live, with its sockets, forever.
        self._watchdog = asyncio.create_task(
            self._close_if_not_connected(
                options.peer_connect_timeout
            )
        )

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
                if not self._closed:
                    # Must actually close the connection: marking it closed
                    # first made close() a no-op, so every failed connection
                    # kept its sockets and tasks until the process restarted.
                    if self._on_close:
                        await self._on_close(self)
                    else:
                        await self.close()

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

    async def _close_if_not_connected(self, timeout):
        try:
            await asyncio.sleep(timeout)

        except asyncio.CancelledError:
            return

        if self._ready or self._closed:
            return

        logs.warning(
            f"[WEBRTC] Peer {self.id} did not connect within "
            f"{timeout:.0f}s, closing it"
        )

        try:
            if self._on_close:
                await self._on_close(self)
            else:
                await self.close()

        except Exception:
            logs.exception("[WEBRTC] Closing a stale peer failed")

    async def close(self):
        if self._closed:
            return

        self._closed = True

        if self._watchdog is not asyncio.current_task():
            self._watchdog.cancel()

        # Stop our relay subscription. Left running it keeps queueing every
        # audio frame for a listener that is gone.
        try:
            self.audio.stop()
        except Exception:
            pass

        try:
            await self.connection.close()

        except Exception:
            logs.exception("[WEBRTC] Closing a connection failed")
