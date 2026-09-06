# pyLiveMusic
A python framework for creating private room for live streaming audio using webrtc.

# Installation
```bash
pip install -U pyLiveMusic
```

# Setup
```python
import asyncio

from pyLiveMusic import Client


async def main():
    client = Client()
    try:
        await client.start()
        await client.run_until_disconnect()
    finally:
        await client.stop()


if __name__ == '__main__':
    asyncio.run(main())
```
