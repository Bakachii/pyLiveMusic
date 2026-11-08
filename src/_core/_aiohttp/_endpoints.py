import re
import gzip
import hashlib

from collections.abc import Callable
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path

from aiohttp import web


@dataclass(frozen=True)
class Endpoint:
    path: str
    html: Path
    css: Path | None = None
    js: Path | None = None
    get: Callable | None = None
    post: Callable | None = None
    root: Path | None = None
    room: bool = False


def route_key(path: str) -> str:
    return re.sub(
        r"\{[^{}]+\}",
        "{}",
        path.rstrip("/") or "/",
    )


def route_name(prefix: str, path: str) -> str:
    path = path.strip("/").replace("/", "-")
    path = re.sub(r"\{([^{}]+)\}", r"\1", path)
    path = re.sub(r"[^A-Za-z0-9_.-]", "-", path)
    path = f"p-{path}" if path else "root"

    return f"custom-{prefix}:{path}"


class _RoomHTMLValidator(HTMLParser):
    def __init__(self):
        super().__init__()

        self.audio_count = 0
        self.audio_id_count = 0
        self.volume_count = 0
        self.status_count = 0

    def _check(self, tag, attrs):
        attributes = {
            name.lower(): value
            for name, value in attrs
        }

        tag = tag.lower()
        element_id = attributes.get("id")

        if tag == "audio":
            self.audio_count += 1

            if element_id == "audio":
                self.audio_id_count += 1

        if element_id == "volume":
            self.volume_count += 1

        if element_id == "status":
            self.status_count += 1

    def handle_starttag(self, tag, attrs):
        self._check(tag, attrs)

    def handle_startendtag(self, tag, attrs):
        self._check(tag, attrs)


def validate_room_endpoint(endpoint: Endpoint):
    html = endpoint.html.read_text(encoding="utf-8")

    parser = _RoomHTMLValidator()
    parser.feed(html)
    parser.close()

    if (
        parser.audio_count != 1
        or parser.audio_id_count != 1
    ):
        raise ValueError(
            'Custom room HTML must contain exactly one '
            '<audio id="audio"> element.'
        )

    if parser.volume_count > 1:
        raise ValueError(
            'Custom room HTML must contain at most one '
            'element with id="volume".'
        )

    if parser.status_count > 1:
        raise ValueError(
            'Custom room HTML must contain at most one '
            'element with id="status".'
        )


def render_endpoint(endpoint: Endpoint) -> str:
    html = endpoint.html.read_text(encoding="utf-8")

    # Custom CSS

    if endpoint.css is not None:
        css = endpoint.css.read_text(encoding="utf-8")
        css = css.replace("</style", r"<\/style")

        style = (
            f"<style>\n"
            f"{css}\n"
            f"</style>\n"
        )

        if "</head>" in html:
            html = html.replace(
                "</head>",
                style + "</head>",
                1,
            )
        else:
            html = style + html

    # Room helpers

    if endpoint.room:
        parser = _RoomHTMLValidator()
        parser.feed(html)
        parser.close()

        room_elements = ""

        if parser.volume_count == 0:
            room_elements += """
<label for="volume">Volume</label>
<input
    id="volume"
    type="range"
    min="0"
    max="1"
    step="0.01"
    value="1"
>
"""

        if parser.status_count == 0:
            room_elements += """
<span id="status">CONNECTING...</span>
"""

        audio_script = (
            '<script src="/static/audio.js?v=3"></script>\n'
        )

        if "</body>" in html:
            html = html.replace(
                "</body>",
                room_elements
                + audio_script
                + "</body>",
                1,
            )
        else:
            html += (
                room_elements
                + audio_script
            )

    # Custom JavaScript

    if endpoint.js is not None:
        js = endpoint.js.read_text(encoding="utf-8")
        js = js.replace("</script", r"<\/script")

        script = (
            f"<script>\n"
            f"{js}\n"
            f"</script>\n"
        )

        if "</body>" in html:
            html = html.replace(
                "</body>",
                script + "</body>",
                1,
            )
        else:
            html += script

    return html


_page_cache = {}


def _signature(endpoint: Endpoint):
    parts = []

    for file in (endpoint.html, endpoint.css, endpoint.js):
        if file is None:
            continue

        info = file.stat()
        parts.append((str(file), info.st_mtime_ns, info.st_size))

    return tuple(parts)


def _cached_page(endpoint: Endpoint):
    """Rendered page + its gzip form, rebuilt only when a source file changes.

    The page used to be re-read from disk and sent uncompressed on every
    request. On a slow or lossy connection (high latency, mobile data) a
    100+ KB page is the difference between opening in 1 s and in 10 s.
    """
    signature = _signature(endpoint)
    cached = _page_cache.get(endpoint)

    if cached is None or cached["signature"] != signature:
        body = render_endpoint(endpoint).encode("utf-8")

        cached = {
            "signature": signature,
            "body": body,
            "gzip": gzip.compress(body, compresslevel=9),
            "etag": '"' + hashlib.sha1(body).hexdigest()[:20] + '"',
        }

        _page_cache[endpoint] = cached

    return cached


async def _html_handler(request, endpoint):
    page = _cached_page(endpoint)

    headers = {
        "ETag": page["etag"],
        "Cache-Control": "no-cache",
        "Vary": "Accept-Encoding",
    }

    if request.headers.get("If-None-Match") == page["etag"]:
        return web.Response(status=304, headers=headers)

    body = page["body"]

    if "gzip" in request.headers.get("Accept-Encoding", "").lower():
        body = page["gzip"]
        headers["Content-Encoding"] = "gzip"

    return web.Response(
        body=body,
        content_type="text/html",
        charset="utf-8",
        headers=headers,
    )


async def _asset_handler(request, endpoint):
    root = (
        endpoint.root
        or endpoint.html.parent
    )

    path = (
        root / request.match_info["asset_path"]
    ).resolve()

    try:
        path.relative_to(root)
    except ValueError:
        raise web.HTTPForbidden()

    if not path.is_file():
        raise web.HTTPNotFound()

    return web.FileResponse(path)


def register_endpoint(app, endpoint):
    if endpoint.get is not None:
        app.router.add_get(
            endpoint.path,
            endpoint.get,
            name=route_name(
                "get",
                endpoint.path,
            ),
        )
    else:
        app.router.add_get(
            endpoint.path,
            lambda request: _html_handler(
                request,
                endpoint,
            ),
            name=route_name(
                "get",
                endpoint.path,
            ),
        )

    if endpoint.post is not None:
        app.router.add_post(
            endpoint.path,
            endpoint.post,
            name=route_name(
                "post",
                endpoint.path,
            ),
        )

    asset_path = (
        endpoint.path.rstrip("/")
        + "/{asset_path:.*}"
    )

    app.router.add_get(
        asset_path,
        lambda request: _asset_handler(
            request,
            endpoint,
        ),
        name=route_name(
            "assets",
            endpoint.path,
        ),
    )