# Custom Endpoints

pyLiveMusic allows you to add your own HTTP endpoints and web pages without modifying the internal pyLiveMusic routes.

A custom endpoint supports:

- HTML
- Optional CSS
- Optional JavaScript
- Optional `GET` handler
- Optional `POST` handler

## Basic Setup

```python
import asyncio

from pyLiveMusic import Client


async def main():
    client = Client()

    client.add_endpoint(
        "/dashboard",
        html="frontend/index.html",
    )

    try:
        await client.start()
        await client.run_until_disconnect()
    finally:
        await client.stop()


asyncio.run(main())
```

The page is available at:

```text
http://localhost:8000/dashboard
```

If no `get` handler is supplied, pyLiveMusic serves the HTML page.

## Endpoint Arguments

```python
client.add_endpoint(
    path,
    html,
    css=None,
    js=None,
    get=None,
    post=None,
)
```

| Argument | Required | Description |
|---|---|---|
| `path` | Yes | URL path for the endpoint. |
| `html` | Yes | Path to the HTML file. |
| `css` | No | Optional CSS file. |
| `js` | No | Optional JavaScript file. |
| `get` | No | Optional aiohttp-style GET handler. |
| `post` | No | Optional aiohttp-style POST handler. |

Example:

```python
client.add_endpoint(
    "/dashboard",
    html="frontend/index.html",
    css="frontend/style.css",
    js="frontend/app.js",
)
```

## HTML

The HTML file is required.

```text
frontend/
├── index.html
├── style.css
└── app.js
```

Example:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard</title>
</head>
<body>
    <h1>My Dashboard</h1>
</body>
</html>
```

## CSS

CSS is optional:

```python
client.add_endpoint(
    "/dashboard",
    html="frontend/index.html",
    css="frontend/style.css",
)
```

The CSS file is automatically inserted into the HTML page.

## JavaScript

JavaScript is optional:

```python
client.add_endpoint(
    "/dashboard",
    html="frontend/index.html",
    js="frontend/app.js",
)
```

The JavaScript file is automatically inserted into the HTML page.

## GET Handler

A GET handler uses the normal aiohttp request format:

```python
from aiohttp import web


async def dashboard(request):
    return web.json_response({
        "message": "Hello",
    })
```

Register it:

```python
client.add_endpoint(
    "/api/dashboard",
    html="frontend/index.html",
    get=dashboard,
)
```

Now:

```text
GET /api/dashboard
```

calls `dashboard()`.

When `get` is supplied, the GET handler controls the response instead of the HTML page.

## POST Handler

A POST handler works the same way:

```python
async def dashboard_post(request):
    data = await request.json()

    return web.json_response({
        "received": data,
    })
```

Register it:

```python
client.add_endpoint(
    "/api/dashboard",
    html="frontend/index.html",
    post=dashboard_post,
)
```

Now:

```text
POST /api/dashboard
```

calls `dashboard_post()`.

## GET and POST Together

Both handlers can be registered on the same endpoint:

```python
from aiohttp import web


async def dashboard(request):
    return web.json_response({
        "message": "GET request",
    })


async def dashboard_post(request):
    data = await request.json()

    return web.json_response({
        "message": "POST request",
        "data": data,
    })


client.add_endpoint(
    "/api/dashboard",
    html="frontend/index.html",
    get=dashboard,
    post=dashboard_post,
)
```

Routes:

```text
GET  /api/dashboard
POST /api/dashboard
```

## Complete Frontend Example

Structure:

```text
tests/new_endpoint/
├── test.py
├── index.html
├── style.css
└── app.js
```

### `index.html`

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Custom Endpoint Test</title>
</head>
<body>
    <h1>Custom Endpoint</h1>

    <button id="hello-button">
        Test GET
    </button>

    <button id="post-button">
        Test POST
    </button>

    <pre id="result"></pre>
</body>
</html>
```

### `style.css`

```css
body {
    margin: 0;
    padding: 40px;
    font-family: Arial, sans-serif;
    background: #111;
    color: white;
}

button {
    padding: 10px 16px;
    margin-right: 8px;
}
```

### `app.js`

```javascript
const result = document.getElementById("result");

document
    .getElementById("hello-button")
    .addEventListener("click", async () => {
        const response = await fetch("/api/hello");
        const data = await response.json();

        result.textContent = JSON.stringify(
            data,
            null,
            2,
        );
    });

document
    .getElementById("post-button")
    .addEventListener("click", async () => {
        const response = await fetch(
            "/api/user",
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    name: "tanji",
                }),
            },
        );

        const data = await response.json();

        result.textContent = JSON.stringify(
            data,
            null,
            2,
        );
    });
```

### `test.py`

```python
import asyncio

from aiohttp import web

from pyLiveMusic import Client


async def get_handler(request):
    return web.json_response({
        "message": "Hello from GET",
    })


async def post_handler(request):
    data = await request.json()

    return web.json_response({
        "message": "Hello from POST",
        "data": data,
    })


async def main():
    client = Client()

    client.add_endpoint(
        "/api/hello",
        html="tests/new_endpoint/index.html",
        css="tests/new_endpoint/style.css",
        js="tests/new_endpoint/app.js",
        get=get_handler,
    )

    client.add_endpoint(
        "/api/user",
        html="tests/new_endpoint/index.html",
        post=post_handler,
    )

    try:
        await client.start()
        await client.run_until_disconnect()
    finally:
        await client.stop()


asyncio.run(main())
```

## Endpoint Rules

### Path

The path must start with `/`.

Valid:

```python
client.add_endpoint(
    "/dashboard",
    html="frontend/index.html",
)
```

Invalid:

```python
client.add_endpoint(
    "dashboard",
    html="frontend/index.html",
)
```

### Route Collisions

Custom endpoints cannot replace pyLiveMusic's internal routes.

This protects room, playback, queue, frontend, and WebRTC functionality.

Dynamic route names are normalized when checking collisions. For example:

```text
/room/{room_id}
/room/{id}
```

are treated as the same route pattern.

### Assets

An endpoint also exposes an asset path below its endpoint:

```text
/dashboard/{asset_path}
```

Only files inside the endpoint's configured HTML directory can be accessed.

Path traversal outside that directory is rejected.

## Complete Example

```python
import asyncio

from aiohttp import web

from pyLiveMusic import Client


async def dashboard_api(request):
    return web.json_response({
        "status": "ok",
        "message": "Dashboard API",
    })


async def dashboard_post(request):
    data = await request.json()

    return web.json_response({
        "status": "ok",
        "data": data,
    })


async def main():
    client = Client()

    client.add_endpoint(
        "/dashboard",
        html="frontend/index.html",
        css="frontend/style.css",
        js="frontend/app.js",
    )

    client.add_endpoint(
        "/api/dashboard",
        html="frontend/index.html",
        get=dashboard_api,
        post=dashboard_post,
    )

    try:
        await client.start()
        await client.run_until_disconnect()
    finally:
        await client.stop()


asyncio.run(main())
```

This creates:

```text
GET  /dashboard
GET  /api/dashboard
POST /api/dashboard
```

Custom endpoints run alongside the normal pyLiveMusic application without replacing its internal routes.