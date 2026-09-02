# pyLiveMusic
A python framework for creating private room for live streaming audio using webrtc.

# Installation
```bash
pip install -U pyLiveMusic
```

# Setup
```python
from pyLiveMusic import Client

server = Client(
    HOST="0.0.0.0",
    PORT=5000,
    AUTH_KEY="124",
)

server.start() 
```
