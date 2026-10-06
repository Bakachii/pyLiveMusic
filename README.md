# pyLiveMusic
A python framework for creating private room for live streaming audio using webrtc.

# Installation

```bash
pip install -U pyLiveMusic
```

### Optional storage backends

<details>
<summary><strong>MongoDB</strong></summary>
<code>pip install -U "pyLiveMusic[mongo]"</code>
</details>

<details>
<summary><strong>Redis</strong></summary>
<code>pip install -U "pyLiveMusic[redis]"</code>
</details>

<details>
<summary><strong>MongoDB + Redis</strong></summary>
<code>pip install -U "pyLiveMusic[all]"</code>
</details>

----------------------------

# Basic Setup
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
----------------------------

# Documentation

- [cURL API reference](docs/curl_methods_for_interaction/README.md) — for HTTP endpoint.
- [Player functions](docs/player_functions/README.md) — the optional Python `Room` / `Queue` / `Playback` API.