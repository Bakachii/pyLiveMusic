import re

from dataclasses import dataclass, field
from pathlib import Path

QUALITY_BITRATES = {
    "low": 48_000,
    "medium": 96_000,
    "high": 128_000,
    "highest": 256_000,
    "peak": 320_000,
}

SAMPLE_RATE = 48_000

# 20 ms of audio at 48 kHz.
FRAME_SAMPLES = 960

# Room is deleted 60 seconds after its queue becomes empty.
ROOM_DELETE_DELAY = 60


STATIC_DIR = (
    Path(__file__).resolve().parents[1]
    / "pyLiveMusic"
    / "_static"
)


# ---------------------------------------------------------------------------
# Limits. Every request that can allocate memory, sockets or CPU is bounded.
# ---------------------------------------------------------------------------

# Same alphabet Telegram allows in a startapp value.
ROOM_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{1,128}$")

MAX_ROOM_NAME = 100
MAX_TITLE = 300
MAX_PATH = 4096
MAX_QUEUE_LENGTH = 500
MAX_ROOMS = 5_000

# Largest request body the server reads (the biggest legitimate one is a
# WebRTC offer, a few KB).
MAX_BODY_BYTES = 64 * 1024
MAX_SDP_BYTES = 32 * 1024

MAX_CANDIDATES_PER_PEER = 64

# A peer that has not reached "connected" after this long is closed.
PEER_CONNECT_TIMEOUT = 40

# Live state is the source of truth; the database only lets rooms survive a
# restart, so a slow or failing database must never block a room.
DB_TIMEOUT = 5.0

# If the audio clock is further behind than this (nobody was pulling frames),
# playback continues in real time instead of fast-forwarding through the gap.
LAG_RESYNC_SECONDS = 1.0

STATS_LOG_EVERY = 600  # seconds


@dataclass
class ServerOptions:
    """Runtime options shared by the HTTP layer and the rooms.

    Built by `Client(...)`; the defaults keep the previous behaviour.
    """

    # WebRTC connectivity
    ice_servers: list = field(default_factory=list)  # [{"urls", "username", "credential"}]
    turn_urls: list = field(default_factory=list)
    turn_secret: str | None = None  # coturn `use-auth-secret`
    turn_username: str | None = None  # or static credentials
    turn_credential: str | None = None
    turn_ttl: int = 86_400

    # Limits (0 = unlimited)
    max_peers_per_room: int = 300
    max_peers_total: int = 2_000
    max_peers_per_ip: int = 0
    peer_connect_timeout: float = PEER_CONNECT_TIMEOUT

    # Security
    trust_proxy: bool = False  # read the client IP from X-Forwarded-For
    allow_private_candidates: bool = False
    media_dirs: list | None = None  # only play files inside these folders
