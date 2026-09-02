import secrets

from aiohttp import web


class Authentication:
    def __init__(self, auth_key: str | None = None):
        self.auth_key = auth_key or secrets.token_urlsafe(32)

    def _get_auth_key(self):
        return self.auth_key

    def _verify(self, request):
        provided_key = request.headers.get("Authorization")

        if not provided_key:
            raise web.HTTPUnauthorized(text="Authentication required")

        if provided_key != f"Bearer {self.auth_key}":
            raise web.HTTPUnauthorized(text="Invalid authentication key")

        return True