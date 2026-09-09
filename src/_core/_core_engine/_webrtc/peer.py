from aiortc import RTCPeerConnection
from aiortc.contrib.media import MediaRelay

from _utils._settings import QUALITY_BITRATES


class Peer:
    def __init__(self, relay, audio_track, quality="high", on_close=None):

        self.connection = RTCPeerConnection()
        print("[WEBRTC] Creating peer")

        self.audio = relay.subscribe(audio_track)
        print("[WEBRTC] Subscribed to audio")

        self.sender = self.connection.addTrack(self.audio)
        print("[WEBRTC] Audio track added")

        self.quality = quality
        self._on_close = on_close
        self._closed = False

        @self.connection.on("connectionstatechange")
        async def connection_state():
            print("[WEBRTC] Connection state:", self.connection.connectionState)

            if self.connection.connectionState in ("closed", "failed"):
                if self._on_close and not self._closed:
                    self._closed = True
                    await self._on_close(self)

        @self.connection.on("iceconnectionstatechange")
        async def ice_state():
            print("[WEBRTC] ICE state:", self.connection.iceConnectionState)

        @self.connection.on("signalingstatechange")
        async def signaling_state():
            print("[WEBRTC] Signaling state:", self.connection.signalingState)


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
        self._closed = True
        await self.connection.close()