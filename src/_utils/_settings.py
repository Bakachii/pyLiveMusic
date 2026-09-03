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


# Path for _static folder
BASE_DIR = Path(__file__).resolve().parents[2]
STATIC_DIR = BASE_DIR / "_static"