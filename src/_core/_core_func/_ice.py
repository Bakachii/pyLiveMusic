import time
import hmac
import base64
import hashlib

DEFAULT_STUN = [
    {"urls": "stun:stun.l.google.com:19302"},
    {"urls": "stun:stun.cloudflare.com:3478"},
]


def browser_ice_servers(options) -> list:
    """ICE servers handed to browsers by GET /api/webrtc/config.

    STUN alone cannot connect users behind carrier-grade or symmetric NAT
    (most mobile networks) or on networks that block UDP. A TURN server
    relays their audio, and over TCP/TLS 443 it also passes UDP-hostile
    networks. Credentials are short-lived: they are derived from a shared
    secret (coturn `use-auth-secret`) and expire on their own.
    """
    servers = [dict(entry) for entry in options.ice_servers] or [
        dict(entry) for entry in DEFAULT_STUN
    ]

    if options.turn_urls:
        username = options.turn_username
        credential = options.turn_credential

        if options.turn_secret:
            username = f"{int(time.time()) + options.turn_ttl}:pylivemusic"
            credential = base64.b64encode(
                hmac.new(
                    options.turn_secret.encode("utf-8"),
                    username.encode("utf-8"),
                    hashlib.sha1,
                ).digest()
            ).decode("ascii")

        if username and credential:
            servers.append({
                "urls": list(options.turn_urls),
                "username": username,
                "credential": credential,
            })

    return servers
