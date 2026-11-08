# WebRTC connectivity (slow or failing connections)

Symptom: users on some networks (typically mobile data) wait a very long time
to connect, or never do, while others connect instantly.

## Why it happens

Audio travels over WebRTC, which tries to open a direct UDP path between the
listener and the server. That works for most people, but not for:

* **Carrier-grade / symmetric NAT** - very common on mobile networks.
* **Networks that block or throttle UDP** - some ISPs, offices, schools.

STUN servers cannot help these users. A **TURN** server can: it relays their
audio, and over TCP/TLS on port 443 it also passes networks that block UDP.

## 1. Run coturn on the same VPS

```bash
sudo apt install coturn
```

`/etc/turnserver.conf`:

```
listening-port=3478
tls-listening-port=443          # needs a certificate, see below
fingerprint
use-auth-secret
static-auth-secret=CHANGE_ME_LONG_RANDOM_STRING
realm=turn.example.com
total-quota=200
no-multicast-peers
no-cli
# Do not let the relay reach your own network:
denied-peer-ip=10.0.0.0-10.255.255.255
denied-peer-ip=172.16.0.0-172.31.255.255
denied-peer-ip=192.168.0.0-192.168.255.255
denied-peer-ip=127.0.0.0-127.255.255.255
# Behind NAT (AWS, GCP, Oracle...): external-ip=PUBLIC_IP/PRIVATE_IP
cert=/etc/letsencrypt/live/turn.example.com/fullchain.pem
pkey=/etc/letsencrypt/live/turn.example.com/privkey.pem
min-port=49160
max-port=49200
```

Open in the firewall: `3478/udp`, `3478/tcp`, `443/tcp` (if port 443 is free;
otherwise use `5349`) and the UDP range `49160-49200`.

## 2. Tell pyLiveMusic about it

```python
client = Client(
    TURN_URLS=[
        "turn:turn.example.com:3478",
        "turns:turn.example.com:443?transport=tcp",
    ],
    TURN_SECRET="CHANGE_ME_LONG_RANDOM_STRING",   # same as static-auth-secret
)
```

Browsers get the list from `GET /api/webrtc/config` with credentials that
expire after 24 h (derived from the secret, nothing to rotate).
For the TgMusicBot set `TURN_URLS` and `TURN_SECRET` in `.env.local`.

## 3. The server itself

* **Docker**: bridge networking hides the server's real address from WebRTC.
  Use `network_mode: host` (or `--network host`) and open the same UDP range
  for the server's own media ports.
* **Firewall**: aiortc uses random UDP ports; allow inbound UDP on the VPS.
* If the VPS cannot reach `stun.l.google.com`, answering an offer is delayed
  by several seconds. Pass your own list (or only TURN entries, to skip STUN)
  with `Client(ICE_SERVERS=[...])`.

## 4. Check

Open `chrome://webrtc-internals` on an affected phone, or use
<https://webrtc.github.io/samples/src/content/peerconnection/trickle-ice/>
with your TURN URL and credentials: a `relay` candidate means TURN works.
`GET /api/health` (with the API key) shows rooms, peers, open files and
memory, and the same numbers are logged every 10 minutes as `[STATS]`.
