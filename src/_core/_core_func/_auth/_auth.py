import hmac
import hashlib
import secrets

from aiohttp import web


class Authentication:
    def __init__(self, auth_key: str | None = None):
        self.generated = not auth_key
        self.auth_key = auth_key or secrets.token_urlsafe(32)

        self._expected = f"Bearer {self.auth_key}".encode("utf-8")

        # Safe to store and to log: it cannot be turned back into the key.
        # Rooms record this as their owner instead of the key itself.
        self.owner_id = hashlib.sha256(
            b"pyLiveMusic-owner:" + self.auth_key.encode("utf-8")
        ).hexdigest()[:16]

    def __repr__(self):
        return f"Authentication(owner_id={self.owner_id})"

    def _get_auth_key(self):
        return self.auth_key

    def is_valid(self, request) -> bool:
        provided = request.headers.get("Authorization")

        if not provided:
            return False

        # Constant-time comparison: no timing side channel on the key.
        return hmac.compare_digest(
            provided.encode("utf-8", "ignore"),
            self._expected,
        )

    def _verify(self, request):
        if not request.headers.get("Authorization"):
            raise web.HTTPUnauthorized(
                text="Authentication required",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not self.is_valid(request):
            raise web.HTTPUnauthorized(
                text="Invalid authentication key",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return True
