---
title: Flask-SocketIO
tags:
  - flask
  - socketio
  - websocket
  - realtime
  - async
  - eventlet
  - gevent
aliases:
  - flask-socketio
  - python-socketio
  - websocket flask
  - realtime flask
related:
  - "[[Celery]]"
  - "[[Flask-Login]]"
  - "[[Flask-JWT-Extended]]"
  - "[[Flask-Caching]]"
  - "[[Flask-CORS]]"
  - "[[Project-Structure]]"
  - "[[Security-Best-Practices]]"
  - "[[Performance-Optimization]]"
created: 2024-01-15
updated: 2024-01-15
---

# Flask-SocketIO

#flask #socketio #websocket #realtime #async #eventlet #gevent

> [!info] WebSocket integration for Flask
> Flask-SocketIO gives your Flask application low-latency, bidirectional, event-driven communication with browsers (and other Socket.IO clients) over WebSockets — with a long-polling fallback when WebSockets are blocked. It is the canonical Flask extension for chat apps, live dashboards, collaborative editors, multiplayer games, and real-time notifications pushed from background jobs (often via [[Celery]]).
>
> Underneath, it wraps the `python-socketio` and `python-engineio` packages and exposes them through a Flask-friendly API: `@socketio.on('event')` handlers, `emit()`/`send()` from server to client, rooms, namespaces, and broadcasting.

Think of Flask-SocketIO as the **radio tower** attached to your Flask app. Normal HTTP is a phone call — you dial a number, exchange words, hang up. WebSockets are an open walkie-talkie channel: once the connection is established, both sides can transmit at any time, with no per-message handshake overhead. Flask-SocketIO builds the *channel* and provides a small vocabulary of *callsigns* (events) so you don't have to invent the radio protocol yourself.

---

## 1. Overview & Metaphor

### What is WebSocket? Why real-time?

The **HTTP protocol is half-duplex and request/response only** — the client must ask before the server can speak. This is fine for documents, but wrong for:

- A chat message arriving the instant the sender hits Enter
- A stock price ticking every 100 ms
- A long-running task reporting progress to the browser that started it
- A second user joining a collaborative document and your cursor appearing in their view

The naive solution — *HTTP polling* (client asks "anything new?" every second) — wastes 99% of requests when nothing is happening and still has up-to-1-second latency when something is.

**WebSocket** (RFC 6455) solves this: a single TCP connection is upgraded from HTTP, then both sides can send frames whenever they want, with negligible overhead (~6 bytes per frame). Latency drops from seconds to milliseconds, and idle cost drops from "request every second" to "one open socket."

### WebSocket vs Server-Sent Events vs Long Polling

| Technique | Direction | Protocol | Browser support | Reconnect | Binary | Best for |
|---|---|---|---|---|---|---|
| **WebSocket** | Bidirectional | WS / TCP | All modern | Manual | Yes | Chat, games, collaboration, real-time control |
| **Server-Sent Events (SSE)** | Server → client only | HTTP | All except old IE | Built-in | No | Live feeds, notifications, dashboards |
| **Long polling** | Bidirectional (faked) | HTTP | Universal | Manual | Yes | Legacy fallback; WebSockets blocked |
| **WebRTC data channels** | Bidirectional (P2P) | SRTP / DTLS | Modern | Manual | Yes | Browser-to-browser, low latency, server-relieved |

> [!note] Socket.IO is *not* a raw WebSocket library
> Socket.IO sits on top of WebSockets (or falls back to long polling) and adds: automatic reconnection, namespacing, rooms, acknowledgements, broadcast, and an event-based message format. If you want raw WebSockets in Python, use `websockets` or `wsproto` directly. If you want batteries-included real-time, use Flask-SocketIO.

### Architecture

```mermaid
flowchart LR
    B[Browser<br/>socket.io.js] -->|HTTP upgrade| N[Nginx / load balancer]
    N --> W1[Flask-SocketIO<br/>gunicorn worker 1]
    N --> W2[Flask-SocketIO<br/>gunicorn worker 2]
    W1 <-->|Redis pub/sub| MQ[(Redis<br/>message queue)]
    W2 <-->|Redis pub/sub| MQ
    MQ <-.emit from outside request.-> C[Celery task<br/>or CLI script]
```

The Redis message queue is what lets multiple Flask workers (and even non-Flask processes like Celery tasks) broadcast to all connected clients. Without it, a client connected to worker-1 will never receive emits from worker-2.

---

## 2. Installation

```bash
# Core
pip install flask-socketio

# Pick exactly ONE async mode by installing the matching driver:
pip install eventlet           # recommended for production
# OR
pip install gevent gevent-websocket
# OR
# (no extra install needed for 'threading' — dev only)
# OR
pip install "python-socketio[asyncio_client]"   # for asyncio mode (advanced)
```

The async mode is auto-detected at startup based on which packages are installed, but you can force it explicitly:

```python
socketio = SocketIO(app, async_mode="eventlet")
```

### Full dev install

```bash
pip install flask flask-socketio eventlet
```

### Production extras

```bash
pip install gunicorn eventlet               # gunicorn worker class
pip install redis                           # for message_queue (multi-worker)
pip install python-engineio                 # bundled, but pin for security
```

> [!warning] Always pin `python-engineio` and `python-socketio`
> These are the low-level libraries and they have had CVEs. Pin them explicitly to a recent version and run `pip-audit` in CI:
> ```bash
> pip install "python-engineio>=4.9,<5" "python-socketio>=5.11,<6"
> ```

---

## 3. Configuration

### The `SocketIO()` constructor

```python
from flask_socketio import SocketIO

socketio = SocketIO(
    app,
    async_mode="eventlet",          # 'threading' | 'eventlet' | 'gevent' | 'asyncio'
    cors_allowed_origins=["https://app.example.com"],
    path="/socket.io",              # URL path (default /socket.io)
    ping_interval=25,               # seconds between keepalive pings
    ping_timeout=20,                # disconnect if no pong within 20s
    max_http_buffer_size=1_000_000, # 1 MiB max message size
    engineio_logger=False,          # verbose transport logs
    logger=False,                   # verbose event logs
    always_connect=False,           # connect even if auth fails (use reject handler)
    json=flask.json,                # JSON serializer (orjson/ujson)
    message_queue="redis://localhost:6379/3",  # multi-worker coordination
    async_handlers=True,            # run handlers in a separate greenlet
)
```

### Full config reference

| Argument | Default | Purpose |
|---|---|---|
| `async_mode` | auto-detected | One of `threading`, `eventlet`, `gevent`, `asyncio` |
| `cors_allowed_origins` | `[]` | List of allowed origins, `"*"`, or a single string |
| `path` | `/socket.io` | URL path the client connects to |
| `ping_interval` | 25 s | Heartbeat interval; <30s recommended to defeat proxies |
| `ping_timeout` | 20 s | Disconnect threshold if no pong |
| `max_http_buffer_size` | 1 MiB | Reject messages larger than this |
| `engineio_logger` | `False` | Engine-level transport debug |
| `logger` | `False` | Event-level debug |
| `always_connect` | `False` | If `False`, connect handler can reject |
| `json` | Flask's json | Custom JSON serializer |
| `message_queue` | `None` | Redis/RabbitMQ URL for multi-worker emit |
| `async_handlers` | `True` | Don't block I/O on slow handler bodies |
| `client_manager` | `None` | Custom pubsub backend (rarely needed) |
| `monitor_clients` | `True` | Periodically clean dead sockets |

### App config keys

```python
app.config["SECRET_KEY"] = "..."                # required for session-based auth
app.config["SESSION_COOKIE_SECURE"] = True      # cookies over HTTPS only
app.config["SESSION_COOKIE_SAMESITE"] = "None"  # cross-origin WS
```

### Application factory pattern

```python
# extensions.py
from flask_socketio import SocketIO
socketio = SocketIO()

# __init__.py
from flask import Flask
from .extensions import socketio

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]

    socketio.init_app(
        app,
        async_mode="eventlet",
        cors_allowed_origins=["https://app.example.com"],
        message_queue=os.environ.get("SOCKETIO_MESSAGE_QUEUE"),
    )

    # Import handlers so they register with the socketio instance
    from . import events  # noqa: F401

    return app
```

---

## 4. Async Modes Compared

The single most important decision in Flask-SocketIO is which **async mode** you run. It dictates everything: how many concurrent clients you can serve, how you deploy, and which libraries are safe to use.

| Mode | Concurrency | CPU-bound? | Monkey-patch? | Best for | Gunicorn worker class |
|---|---|---|---|---|---|
| **threading** | ~10–50 per process | Yes (OS threads) | No | Dev only; tiny apps | `gthread` |
| **eventlet** | 1000s per process | No | Yes (auto) | Production I/O-bound apps | `eventlet` |
| **gevent** | 1000s per process | No | Yes (manual) | Same as eventlet | `gevent` (with `gevent-websocket`) |
| **asyncio** | 1000s per process | No | No | Modern async codebases; mixed with `aiohttp` | `uvicorn` (with `engineio` ASGI) |

### Mermaid: async-mode decision tree

```mermaid
flowchart TD
    A[Choose async mode] --> B{Production?}
    B -->|no, just dev| T[threading]
    B -->|yes| C{Need CPU-bound work in handlers?}
    C -->|yes| T2[threading<br/>low concurrency]
    C -->|no| D{Existing async codebase<br/>e.g. aiohttp, asyncpg?}
    D -->|yes| AS[asyncio + ASGI]
    D -->|no| E{Team familiarity?}
    E -->|eventlet| EV[eventlet]
    E -->|gevent| GV[gevent + gevent-websocket]
```

### Why eventlet/gevent?

WebSockets hold a connection open for the lifetime of the user's session — minutes to hours. A traditional threaded server is capped at ~50 concurrent sockets per process because each thread consumes ~8 MB of stack. Greenlets (eventlet/gevent) use ~10 KB per coroutine, so a single process can hold 10,000+ open sockets.

### Monkey-patching

Eventlet and gevent achieve concurrency by **monkey-patching** the standard library's blocking I/O calls (socket, ssl, threading, subprocess) to use cooperative scheduling instead. This means *every* I/O library you import (requests, psycopg2, redis-py, SQLAlchemy's connection pool) is silently converted to non-blocking.

> [!danger] Monkey-patch before any other import
> The patch must be the **very first** line of your entry point. If `flask`, `sqlalchemy`, `redis`, or `requests` is imported first, the patch silently misses those modules and you get deadlocks.
>
> ```python
> # CORRECT — at the top of wsgi.py or whatever your entry point is
> import eventlet
> eventlet.monkey_patch()
>
> from myapp import create_app
> app = create_app()
> ```

### Threading mode gotchas

`threading` mode works out of the box with no monkey-patching — but it's capped at the number of worker threads. Use it only for local development:

```python
socketio = SocketIO(app, async_mode="threading")
socketio.run(app, host="0.0.0.0", port=5000)
```

### Asyncio mode (advanced)

For greenfield codebases that already speak `async`/`await`, `python-socketio` ships an ASGI app you can mount:

```python
# asgi.py
import socketio
from myapp import create_app

flask_app = create_app()
sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")
asgi_app = socketio.ASGIApp(sio, other_asgi_app=flask_app)

@sio.event
async def connect(sid, environ, auth):
    await sio.emit("hello", {"sid": sid}, to=sid)
```

```bash
uvicorn myapp.asgi:asgi_app --workers 4
```

This bypasses the Flask-SocketIO wrapper; you talk directly to `python-socketio`'s `AsyncServer`. You lose the Flask request/session integration, so most apps stay on eventlet for simplicity.

---

## 5. Basic Usage

### Server-side handler

```python
# events.py
from flask_socketio import emit, join_room, leave_room
from .extensions import socketio

@socketio.on("connect")
def handle_connect(auth):
    print("Client connected")

@socketio.on("disconnect")
def handle_disconnect():
    print("Client disconnected")

@socketio.on("message")             # plain string messages
def handle_message(msg):
    print(f"Message: {msg}")
    emit("message", f"echo: {msg}")  # send back to same client

@socketio.on("my_event")            # JSON events
def handle_my_event(data):
    emit("my_response", {"received": data})
```

### Client-side (browser)

```html
<!-- templates/chat.html -->
<script src="https://cdn.socket.io/4.7.5/socket.io.min.js"></script>
<script>
  const socket = io("https://app.example.com", {
    path: "/socket.io",
    transports: ["websocket"],
    auth: { token: "{{ jwt_token }}" },
  });

  socket.on("connect", () => console.log("connected", socket.id));
  socket.on("disconnect", (reason) => console.log("disconnected:", reason));

  socket.on("my_response", (data) => console.log("server:", data));

  // Send an event
  socket.emit("my_event", { hello: "world" });

  // Send with acknowledgement callback
  socket.emit("ping", { t: Date.now() }, (ack) => {
    console.log("server acked in", Date.now() - ack.t, "ms");
  });
</script>
```

> [!tip] Pin both client and server to the same major version
> Socket.IO 4.x client cannot talk to a Socket.IO 2.x server (protocol mismatch). Flask-SocketIO 5.x bundles python-socketio 5.x and is compatible with browser client 4.x. Pin your CDN URL:
> ```html
> <script src="https://cdn.socket.io/4.7.5/socket.io.min.js"
>         integrity="sha384-..." crossorigin="anonymous"></script>
> ```

### `emit()` vs `send()`

| Function | What it does |
|---|---|
| `emit(event, data)` | Send a named event with JSON data |
| `send(data)` | Send a `message` event (the default event name) |
| `emit(event, callback=fn)` | Request acknowledgement from client |
| `emit(..., broadcast=True)` | Send to *all* connected clients (not just the sender) |
| `emit(..., to=room)` | Send to everyone in a room |
| `emit(..., namespace="/admin")` | Send to a namespace |
| `emit(..., include_self=False)` | Broadcast to room except sender |

```python
@socketio.on("chat")
def handle_chat(msg):
    emit("chat", msg)                              # to sender only
    emit("chat", msg, broadcast=True)              # to everyone
    emit("chat", msg, to="room_42")                # to a room
    emit("chat", msg, to="room_42", include_self=False)  # everyone but sender
```

### Mermaid: client connect → join → message → disconnect

```mermaid
sequenceDiagram
    participant B as Browser
    participant S as Flask-SocketIO server

    B->>S: HTTP Upgrade: WebSocket
    S-->>B: 101 Switching Protocols
    B->>S: connect (auth token)
    S-->>B: connect ack

    B->>S: emit('join', {room: 'general'})
    S->>S: join_room('general')
    S-->>B: emit('joined', {room: 'general'})

    B->>S: emit('chat', {msg: 'hi'})
    S->>S: handler runs
    S-->>B: emit('chat', {msg:'hi', from:'alice'})   (broadcast to room)

    Note over B: tab closes
    B->>S: TCP FIN
    S->>S: handle_disconnect()
    S-->>S: leave_room('general') (auto)
```

---

## 6. Intermediate Patterns

### Namespaces

A namespace is a separate channel multiplexed over one WebSocket. Use them to separate concerns without opening multiple sockets:

```python
@socketio.on("connect", namespace="/chat")
def chat_connect(auth):
    emit("ready", {"version": 2}, namespace="/chat")

@socketio.on("message", namespace="/chat")
def chat_message(msg):
    emit("message", msg, namespace="/chat", broadcast=True)

@socketio.on("connect", namespace="/admin")
def admin_connect(auth):
    if not current_user.is_admin:
        return False  # reject connection
    emit("stats", get_stats(), namespace="/admin")
```

```js
const chat = io("/chat", { transports: ["websocket"] });
const admin = io("/admin", { transports: ["websocket"], auth: { token } });
```

### Rooms

A room is a server-side set of `sid`s (session ids). Anyone in a room receives emits addressed to it. Use rooms for chat channels, per-user private channels, document collaboration, etc.

```python
from flask_socketio import join_room, leave_room, rooms
from flask_login import current_user

@socketio.on("join")
def on_join(data):
    room = data["room"]
    join_room(room)
    emit("system", f"{current_user.name} joined {room}", to=room)

@socketio.on("leave")
def on_leave(data):
    room = data["room"]
    leave_room(room)
    emit("system", f"{current_user.name} left {room}", to=room)

@socketio.on("chat")
def on_chat(data):
    room = data["room"]
    emit("chat", {"from": current_user.name, "text": data["text"]},
         to=room, include_self=True)
```

> [!tip] Auto-join a per-user room on connect
> For private messages, join every user to a room named `f"user_{current_user.id}"` on connect. Emitting to that room delivers the message even if the user has multiple tabs open — and only to *that* user.
> ```python
> @socketio.on("connect")
> def on_connect(auth):
>     join_room(f"user_{current_user.id}")
> ```

### Mermaid: rooms vs namespaces — design map

```mermaid
mindmap
  root((Realtime routing))
    Rooms
      server-side set of sids
      join_room / leave_room
      free to join many
      one socket per client
      use for
        per-user private channel
        chat channels
        doc collaboration
    Namespaces
      separate multiplexed channel
      own connect/disconnect
      own auth handler
      own error handler
      use for
        /chat /admin /imports
        separate concerns
        independent auth
    Broadcast
      all connected clients
      optional namespace filter
      optional room filter
      include_self toggle
    Acknowledgements
      request/response over push
      client callback
      useful for confirmed delivery
```

### Broadcasting

Broadcasting sends to *every* connected client (optionally across namespaces or rooms):

```python
@socketio.on("shout")
def on_shout(msg):
    socketio.emit("broadcast", msg)   # every client, every namespace
```

### Mermaid: message-type distribution in a busy chat app

```mermaid
pie showData
    title Event traffic by type (24h sample)
    "chat message" : 45
    "typing indicator" : 25
    "presence join/leave" : 12
    "ack ping" : 10
    "system / error" : 5
    "binary file chunk" : 3
```

`socketio.emit()` (the method on the extension) differs from the `emit()` import — it doesn't require request context and works from outside handlers (e.g. from a Celery task).

### Mermaid: connection lifecycle state machine

```mermaid
stateDiagram-v2
    [*] --> Disconnected
    Disconnected --> Connecting: io(url, {auth})
    Connecting --> Connected: 101 Switching Protocols + ack
    Connecting --> Rejected: ConnectionRefused
    Rejected --> [*]
    Connected --> InRoom: emit('join')
    InRoom --> InRoom: emit('chat') / emit('leave')
    InRoom --> Connected: leave_room()
    Connected --> Reconnecting: ping timeout / transport close
    Reconnecting --> Connected: reconnect succeeds
    Reconnecting --> Disconnected: max retries exceeded
    Connected --> Disconnected: socket.close()
    Disconnected --> [*]
```

### Connection events & auth

```python
from flask_login import current_user, login_user
from flask_socketio import ConnectionRefusedError

@socketio.on("connect")
def connect(auth):
    """Validate the client before accepting the connection."""
    token = (auth or {}).get("token")
    if not token:
        raise ConnectionRefusedError("missing token")
    user = decode_jwt(token)
    if not user:
        raise ConnectionRefusedError("invalid token")
    login_user(user)         # populate current_user for this socket
    join_room(f"user_{user.id}")
    emit("ready", {"sid": request.sid})
```

> [!danger] Don't rely on `session` for WebSocket auth
> The Flask `session` cookie is sent with the HTTP upgrade request, so it *does* populate `session` in the connect handler. But:
> 1. Cross-origin WebSockets don't send cookies unless `withCredentials: true` on the client AND `SameSite=None; Secure` on the cookie.
> 2. The session is not refreshed mid-connection — if the user logs out via a normal HTTP route, their existing socket stays authenticated until they reconnect.
> Use a token in the `auth` payload (sent every reconnect) and re-validate on each connect.

### Error handling

```python
from flask_socketio import ConnectionRefusedError

@socketio.on_error()
def default_error_handler(e):
    app.logger.exception("Socket.IO error: %s", e)
    emit("error", {"message": "internal error"})

@socketio.on_error("/chat")
def chat_error_handler(e):
    emit("error", {"namespace": "/chat", "message": str(e)}, namespace="/chat")

@socketio.on_error_handler
def global_handler(e):
    """Catches errors raised outside any handler."""
    app.logger.exception("Global socketio error: %s", e)
```

### Acknowledgements (request/response over WebSocket)

```python
@socketio.on("compute")
def on_compute(data, ack_callback=None):
    result = expensive_computation(data)
    if ack_callback:
        ack_callback({"result": result})   # calls client's callback
```

```js
socket.emit("compute", { x: 1, y: 2 }, (ack) => {
  console.log("server computed:", ack.result);
});
```

Acknowledgements are how you do **request/response over a push channel** — useful when the client needs confirmation that the server received and processed an event.

### Handling messages from outside the request context

The classic pattern — emit from a Celery task, a CLI script, or another worker process — uses the `message_queue`:

```python
# extensions.py
socketio = SocketIO(message_queue=os.environ["SOCKETIO_MESSAGE_QUEUE"])

# In any process (Celery worker, CLI script, separate Flask process):
from myapp.extensions import socketio

def progress_callback(task_id, percent):
    socketio.emit("progress",
                  {"task_id": task_id, "percent": percent},
                  namespace="/tasks",
                  room=f"task_{task_id}")
```

> [!note] `room` is the Flask-SocketIO alias for `to`
> When using `socketio.emit()` (the standalone method), the parameter is called `room`. When using `emit()` inside a handler, it's `to`. They're the same thing.

---

## 7. Advanced Usage

### Multi-worker scaling with a message queue

Single-process SocketIO works out of the box. The moment you run a second gunicorn worker (or a second server), you need a **message queue** so emits from one process reach clients connected to another.

```python
socketio = SocketIO(
    app,
    async_mode="eventlet",
    message_queue="redis://redis:6379/3",
)
```

Now `socketio.emit()` publishes to the Redis pub/sub channel `socketio`; every Flask worker subscribes and delivers to its locally-connected clients.

```mermaid
flowchart LR
    C1[Client A] -.WS.-> W1[Worker 1]
    C2[Client B] -.WS.-> W2[Worker 2]
    C3[Client C] -.WS.-> W2

    W1 <-->|publish/subscribe| R[(Redis<br/>socketio channel)]
    W2 <-->|publish/subscribe| R

    T[Celery task] -->|socketio.emit| R
```

> [!warning] Without `message_queue`, emits are local-only
> If you forget to set `message_queue` in production, your Celery tasks will silently emit to a local SocketIO server that has zero clients connected. Symptom: "my background task says it emitted, but the browser never sees it." Always check `socketio.server.eio.async_handlers` is True and `message_queue` is set.

### Mermaid: cross-worker emit via Redis pub/sub

```mermaid
sequenceDiagram
    participant T as Celery task<br/>(worker process)
    participant R as Redis pub/sub
    participant W1 as Gunicorn worker 1
    participant W2 as Gunicorn worker 2
    participant C1 as Browser A<br/>on worker 1
    participant C2 as Browser B<br/>on worker 2

    Note over C1,C2: both joined room "project:42"
    T->>R: socketio.emit('task:updated',<br/>payload, room='project:42')
    R-->>W1: publish to channel 'socketio'
    R-->>W2: publish to channel 'socketio'
    W1->>W1: lookup local sids in 'project:42'
    W2->>W2: lookup local sids in 'project:42'
    W1->>C1: WS frame 'task:updated'
    W2->>C2: WS frame 'task:updated'
    Note over T: emits without owning<br/>a Flask app context
```

### RabbitMQ as message queue

```python
socketio = SocketIO(
    app,
    message_queue="amqp://guest:guest@rabbitmq:5672//",
)
```

Useful when your team already runs RabbitMQ for Celery and doesn't want to add Redis just for SocketIO.

### Custom client manager

For exotic backends (Kafka, NATS, Kubernetes-specific service discovery), subclass `socketio.KombuManager` or `socketio.BaseManager`:

```python
from socketio import KombuManager

class MyManager(KombuManager):
    def _publish(self, data):
        # custom routing
        ...

socketio = SocketIO(app, client_manager=MyManager("amqp://..."))
```

### Sticky sessions at the load balancer

WebSocket upgrades are *stateful* — once a client connects to worker-3, all subsequent frames on that TCP connection must go to worker-3. Most cloud load balancers support this via:

- **AWS ALB**: stickiness enabled, target type = instance (not IP)
- **Nginx**: `ip_hash;` directive
- **HAProxy**: `balance source`
- **Cloudflare**: "Session Affinity" with cookie

Without sticky sessions, your ALB will route the upgrade to worker-1 and the next frame to worker-2 — which doesn't have that socket — and the connection drops.

### Auth integration patterns

#### With [[Flask-Login]]

```python
from flask_login import current_user, login_user
from itsdangerous import URLSafeTimedSerializer

@socketio.on("connect")
def connect(auth):
    if not current_user.is_authenticated:
        # Try to log in from the auth payload
        token = (auth or {}).get("token")
        if not token:
            raise ConnectionRefusedError("unauthorized")
        try:
            serializer = URLSafeTimedSerializer(current_app.secret_key)
            user_id = serializer.loads(token, max_age=3600)
            user = User.query.get(user_id)
            login_user(user)
        except Exception:
            raise ConnectionRefusedError("invalid token")
    join_room(f"user_{current_user.id}")
```

#### With [[Flask-JWT-Extended]]

```python
from flask_jwt_extended import decode_token, verify_jwt_in_request

@socketio.on("connect")
def connect(auth):
    token = (auth or {}).get("token")
    if not token:
        raise ConnectionRefusedError("missing token")
    try:
        decoded = decode_token(token)
        # Optionally check fresh token, blacklist, etc.
        request.sid_user = decoded["sub"]
    except Exception:
        raise ConnectionRefusedError("invalid token")
```

### Server-initiated emits from Celery tasks

Real-time progress from background work is the killer use case for Flask-SocketIO + Celery:

```python
# tasks.py
from celery import shared_task
from .extensions import socketio

@shared_task(bind=True)
def long_import(self, file_id, user_id):
    total = sum(1 for _ in open(file_path(file_id)))
    for i, row in enumerate(csv.reader(open(file_path(file_id)))):
        process_row(row)
        if i % 100 == 0:
            self.update_state(state="PROGRESS", meta={"current": i, "total": total})
            socketio.emit("import_progress",
                          {"file_id": file_id, "current": i, "total": total},
                          namespace="/imports",
                          room=f"user_{user_id}")
    socketio.emit("import_done",
                  {"file_id": file_id, "rows": total},
                  namespace="/imports",
                  room=f"user_{user_id}")
```

```js
const sock = io("/imports", { transports: ["websocket"], auth: { token } });
sock.on("import_progress", (d) => setProgress(d.current / d.total));
sock.on("import_done", (d) => alert(`Imported ${d.rows} rows!`));
```

See [[Celery]] for the full task queue architecture.

### Handling disconnect cleanly

When a client disconnects (tab close, network drop), Flask-SocketIO fires `disconnect` and automatically removes them from any rooms they joined. But if you maintained per-connection state (typing indicators, presence), you must clean it up yourself:

```python
# In-memory presence (use Redis in production)
PRESENCE = {}  # {room: {sid: user_id}}

@socketio.on("join")
def on_join(data):
    room = data["room"]
    join_room(room)
    PRESENCE.setdefault(room, {})[request.sid] = current_user.id
    emit("presence", {"users": list(set(PRESENCE[room].values()))},
         to=room, include_self=True)

@socketio.on("disconnect")
def on_disconnect():
    for room, members in list(PRESENCE.items()):
        if request.sid in members:
            user_id = members.pop(request.sid)
            leave_room(room)
            emit("presence", {"users": list(set(members.values()))},
                 to=room)
```

### Per-connection state via `request.sid` and `environ`

```python
from flask import request

@socketio.on("connect")
def connect(auth):
    environ = request.environ
    ip = environ.get("REMOTE_ADDR")
    user_agent = environ.get("HTTP_USER_AGENT")
    request.sid  # unique per connection
```

`request.sid` is the unique connection identifier. Store any per-connection state keyed by it.

### Binary messages

```python
@socketio.on("file_chunk")
def on_chunk(data):
    # data is bytes when client emits with {binary: true}
    save_chunk(data)
    emit("chunk_ack", b"ok")  # binary ack
```

```js
socket.emit("file_chunk", arrayBuffer, (ack) => {
  // ack is an ArrayBuffer
});
```

### Catching all events

```python
@socketio.on("*")
def catch_all(event, *args):
    app.logger.warning("Unknown event: %s args=%s", event, args)
    emit("error", {"unknown_event": event})
```

Useful for debugging or for building generic proxies.

---

## 8. Common Pitfalls & Troubleshooting

### Mermaid: troubleshooting flowchart

```mermaid
flowchart TD
    A[WS not connecting] --> B{Browser console error?}
    B -->|CORS| C[Set cors_allowed_origins]
    B -->|404 on /socket.io| D[Check path and Nginx proxy]
    B -->|no error but stuck connecting| E{sticky sessions?}
    E -->|no| E1[Enable ip_hash at LB]
    E -->|yes| F{message_queue set?}
    F -->|no, multi-worker| F1[Set message_queue]
    F -->|yes| G[Check engineio logs]

    H[Emit not received] --> I{in request context?}
    I -->|yes, emit called| I1[Use socketio.emit not emit]
    I -->|no, from Celery| J{message_queue set in producer?}
    J -->|no| J1[Set in both]
    J -->|yes| K{room name match?}
    K -->|no| K1[Verify room/sid]
    K -->|yes| L[Check namespace match]

    M[Connection drops every 25s] --> N[Proxy idle timeout < ping_interval]
    N --> N1[Set proxy_read_timeout 60s in Nginx]
```

### Symptom / cause / fix table

| Symptom | Likely cause | Fix |
|---|---|---|
| `CORS policy blocked` in browser | `cors_allowed_origins` not set | Pass list of origins (or `"*"` for dev) |
| 400 Bad Request on `GET /socket.io/` | Wrong `path` or reverse proxy strips path | Match `path` in client and server; Nginx `proxy_pass` must end with `/` |
| Client stuck on "polling" never upgrading | `transports: ["websocket"]` not set, or proxy strips `Upgrade` header | Add `proxy_set_header Upgrade $http_upgrade;` to Nginx |
| `RuntimeError: You need to use the eventlet or gevent server` | Used `app.run()` instead of `socketio.run(app)` | Use `socketio.run(app)` in dev |
| Emit from Celery task silently goes nowhere | `message_queue` not set on producer's SocketIO instance | Set `message_queue` in extensions.py and ensure Celery imports the same instance |
| Connection drops every 25–60 s | Proxy idle timeout shorter than `ping_interval` | Nginx: `proxy_read_timeout 60s;` |
| `gevent.websocket` not found | Missing `gevent-websocket` package | `pip install gevent gevent-websocket` |
| `socket` is undefined in browser | Missing `<script src="socket.io.js">` | Include CDN or `npm install socket.io-client` |
| 100% CPU in worker with no traffic | `engineio_logger=True` in production | Set to `False` |
| Auth `ConnectionRefused` raises on client but server keeps socket | `always_connect=True` | Set `always_connect=False` (default) |
| Multiple browser tabs open same socket | Each tab opens its own connection (expected) | Use a per-user room to broadcast to all tabs |
| Monkey-patch warning despite `eventlet.monkey_patch()` | Imported Flask/SQLAlchemy before patch | Put `eventlet.monkey_patch()` at the very top of the entry point |

### The big four killers

> [!danger] 1. CORS not configured for WebSockets
> The browser's same-origin policy applies to WebSocket upgrades. If your client is at `https://app.example.com` and the server at `https://api.example.com`, you must set `cors_allowed_origins=["https://app.example.com"]`. Without it, the upgrade fails silently (you'll see `CORS error` in browser devtools). See [[Flask-CORS]] for the general CORS background.

> [!danger] 2. Monkey-patching order
> If `eventlet.monkey_patch()` runs *after* any standard-library I/O import, those modules use the original blocking implementations and your worker hangs at the first DB query. Always put the patch as line 1 of your `wsgi.py`.

> [!danger] 3. Session/auth doesn't work in WebSocket
> The Flask `session` cookie is sent only on the initial HTTP upgrade. If your cookie is `SameSite=Lax` and the WebSocket is cross-origin, it's blocked. Use explicit token auth in the `auth` payload.

> [!danger] 4. Missing sticky sessions at the load balancer
> Without sticky sessions, the LB routes the upgrade to worker-1 and subsequent frames to worker-2 — which doesn't have the socket. Connection drops after 1 ping cycle. Configure `ip_hash` (Nginx) or sticky cookies (ALB).

---

## 9. Best Practices

### Use `async_mode="eventlet"` in production

Eventlet is the most battle-tested async mode for Flask-SocketIO. Gevent works too but requires the `gevent-websocket` companion package and slightly more config.

### Set `transports: ["websocket"]` on the client

Letting the client fall back to long-polling hides real WebSocket problems and adds latency. Force WebSocket transport; if it fails, you want to know immediately, not silently degrade.

```js
const socket = io({ transports: ["websocket"], upgrade: false });
```

### Keep handlers fast

Handlers run in the socket's event loop. A handler that takes 1 second blocks every other connection on that worker. Offload slow work to Celery — see [[Celery]] — and emit progress back via `socketio.emit()`.

### Always set a `ping_interval` shorter than your proxy timeout

```python
socketio = SocketIO(app, ping_interval=25, ping_timeout=20)
```

```nginx
location /socket.io/ {
    proxy_read_timeout 60s;   # > ping_interval (25) + ping_timeout (20)
}
```

### Use Redis (or RabbitMQ) message queue from day one

Even if you start with a single worker, set `message_queue` so scaling out later is a config change, not a code change. It also unlocks Celery task emits "for free."

### Authenticate on every (re)connect

```python
@socketio.on("connect")
def connect(auth):
    user = verify_token(auth["token"])  # always re-check
    if not user:
        raise ConnectionRefusedError("invalid token")
    login_user(user)
    join_room(f"user_{user.id}")
```

This ensures reconnects after token refresh work and that logged-out users can't keep their socket.

### Use rooms, not namespaces, for per-user channels

A namespace opens a separate socket per namespace on the client (more overhead). A room is just a server-side set — multiple rooms per socket are free. Use `/` (default namespace) + per-user rooms.

### Rate-limit incoming events

A malicious client can flood your server with events. Use a custom decorator or [[Flask-Limiter]]-style token bucket:

```python
from collections import defaultdict
from time import time

LAST = defaultdict(float)

def rate_limit(max_per_sec=5):
    def deco(fn):
        def wrapped(*args, **kwargs):
            sid = request.sid
            now = time()
            if now - LAST[sid] < 1 / max_per_sec:
                raise ConnectionRefusedError("rate limit")
            LAST[sid] = now
            return fn(*args, **kwargs)
        return wrapped
    return deco

@socketio.on("chat")
@rate_limit(max_per_sec=2)
def on_chat(msg): ...
```

### Persist presence in Redis, not in-process

If you use in-memory `dict` for presence, restart loses everything and multi-worker instances disagree. Use Redis hash sets keyed by room.

### Set `max_http_buffer_size` to defend against abuse

The default 1 MiB is generous for chat. Lower it to e.g. 100 KB if your protocol only ever sends small events.

### Always log disconnect reasons

```python
@socketio.on("disconnect")
def on_disconnect(reason=None):
    app.logger.info("disconnect sid=%s reason=%s", request.sid, reason)
```

Disconnect reasons (`transport close`, `transport error`, `ping timeout`, `client namespace disconnect`) are invaluable for debugging production issues.

---

## 10. Integration with Other Extensions

### [[Celery]]

The dominant pattern: Celery task runs in background, emits progress to the user's room via the message queue. See §7 for a complete example.

### [[Flask-Login]]

Re-use `current_user` inside handlers — but re-authenticate on every `connect`:

```python
@socketio.on("connect")
def connect(auth):
    if not current_user.is_authenticated:
        # Re-auth via token
        ...
    join_room(f"user_{current_user.id}")
```

### [[Flask-JWT-Extended]]

Pass JWT in the `auth` payload, decode it in the connect handler. See §7.

### [[Flask-CORS]]

`cors_allowed_origins` on `SocketIO()` is separate from your Flask-CORS config — set both. See [[Flask-CORS]] for the underlying CORS threat model.

### [[Flask-Caching]]

Cache expensive data fetched in handlers:

```python
@socketio.on("request_dashboard")
def on_dash():
    data = cache.get("dashboard:v1")
    if data is None:
        data = compute_dashboard()
        cache.set("dashboard:v1", data, timeout=30)
    emit("dashboard", data)
```

### [[Flask-Limiter]]

You can't directly use Flask-Limiter on socket handlers (they're not HTTP routes), but you can apply its decorator to the underlying `connect` HTTP endpoint — or roll your own (see §9).

### [[Marshmallow]]

Validate incoming event payloads with Marshmallow schemas:

```python
from marshmallow import Schema, fields, ValidationError

class ChatSchema(Schema):
    room = fields.String(required=True)
    text = fields.String(required=True, validate=validate.Length(max=500))

@socketio.on("chat")
def on_chat(data):
    try:
        msg = ChatSchema().load(data)
    except ValidationError as err:
        return emit("error", err.messages)
    emit("chat", msg, to=msg["room"])
```

---

## 11. Real-World Example

A complete, runnable single-file Flask-SocketIO chat application: rooms, typing indicators, user join/leave, auth via simple token, broadcasting, and a Celery hook for fake AI replies.

```python
# chat.py — single-file Flask-SocketIO chat
import os, time, threading
from datetime import datetime, timezone
from flask import Flask, request, jsonify, render_template_string
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    ConnectionRefusedError
from flask_login import LoginManager, UserMixin, login_user, current_user, \
    login_required

# --- App ---
app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret")
login_manager = LoginManager(app)

# --- In-memory stores (replace with Redis in production) ---
USERS = {"alice": {"id": 1, "name": "Alice", "token": "tok-alice"},
         "bob":   {"id": 2, "name": "Bob",   "token": "tok-bob"}}
TYPING = {}        # {room: {user_id: timestamp}}
HISTORY = {}       # {room: [msg, ...]}

# --- Flask-Login ---
class User(UserMixin):
    def __init__(self, data): self.__dict__.update(data)

@login_manager.user_loader
def load_user(uid):
    for u in USERS.values():
        if str(u["id"]) == str(uid):
            return User(u)
    return None

def authenticate(token):
    for u in USERS.values():
        if u["token"] == token:
            return User(u)
    return None

# --- SocketIO ---
socketio = SocketIO(
    app,
    async_mode="threading",                      # dev only — use eventlet in prod
    cors_allowed_origins="*",
    ping_interval=25,
    ping_timeout=20,
    message_queue=os.environ.get("SOCKETIO_MQ"),  # None → single-process
)

# --- Connection lifecycle ---
@socketio.on("connect")
def connect(auth):
    token = (auth or {}).get("token")
    user = authenticate(token)
    if not user:
        raise ConnectionRefusedError("invalid token")
    login_user(user)
    join_room(f"user_{user.id}")
    emit("ready", {"sid": request.sid, "user": user.name,
                   "server_time": datetime.now(timezone.utc).isoformat()})

@socketio.on("disconnect")
def disconnect():
    if not current_user.is_authenticated:
        return
    # Remove from any room they were in
    for room in list(HISTORY.keys()):
        leave_room(room)
        emit("system", {"type": "left", "user": current_user.name,
                        "room": room, "ts": _now()}, to=room)

# --- Chat ---
@socketio.on("join")
def on_join(data):
    room = data["room"]
    join_room(room)
    history = HISTORY.setdefault(room, [])
    emit("history", history, to=request.sid)
    emit("system", {"type": "joined", "user": current_user.name,
                    "room": room, "ts": _now()}, to=room, include_self=False)

@socketio.on("leave")
def on_leave(data):
    room = data["room"]
    leave_room(room)
    emit("system", {"type": "left", "user": current_user.name,
                    "room": room, "ts": _now()}, to=room)

@socketio.on("chat")
def on_chat(data):
    room = data["room"]
    text = data["text"][:500]
    msg = {"user": current_user.name, "text": text, "ts": _now(),
           "room": room}
    HISTORY.setdefault(room, []).append(msg)
    HISTORY[room] = HISTORY[room][-100:]   # keep last 100
    emit("chat", msg, to=room, include_self=True)
    # Clear typing indicator
    TYPING.setdefault(room, {}).pop(current_user.id, None)
    emit("typing", {"room": room, "users": _typing_users(room)}, to=room)

# --- Typing ---
@socketio.on("typing")
def on_typing(data):
    room = data["room"]
    TYPING.setdefault(room, {})[current_user.id] = time.time()
    emit("typing", {"room": room, "users": _typing_users(room)},
         to=room, include_self=False)

# --- Acknowledged ping (request/response over WS) ---
@socketio.on("ping_server")
def on_ping(data, ack=None):
    if ack:
        ack({"pong": True, "received_at": _now(), "echo": data})

# --- Helpers ---
def _now():
    return datetime.now(timezone.utc).isoformat()

def _typing_users(room):
    cutoff = time.time() - 3
    return [u for u, t in TYPING.get(room, {}).items() if t > cutoff]

# --- HTTP routes ---
@app.get("/")
def index():
    return render_template_string(HTML_TEMPLATE)

@app.post("/login")
def login():
    name = request.json["name"].lower()
    if name not in USERS:
        return jsonify({"error": "unknown user"}), 404
    return jsonify({"token": USERS[name]["token"], "name": USERS[name]["name"]})

# --- Background emit (mimics a Celery task) ---
def fake_ai_reply(room, after=2.0):
    """Pretend a Celery worker is emitting back after a delay."""
    time.sleep(after)
    with app.app_context():
        socketio.emit("chat", {"user": "AI", "text": "Hi there!",
                               "ts": _now(), "room": room}, to=room)

@socketio.on("ask_ai")
def on_ask_ai(data):
    room = data["room"]
    threading.Thread(target=fake_ai_reply, args=(room,), daemon=True).start()
    emit("system", {"type": "ai_thinking", "room": room}, to=room)

# --- HTML / JS client ---
HTML_TEMPLATE = """<!doctype html>
<html><head><meta charset="utf-8"><title>Chat</title>
<script src="https://cdn.socket.io/4.7.5/socket.io.min.js"></script>
<style>body{font-family:sans-serif;margin:2em}#log{height:300px;overflow:auto;
border:1px solid #ccc;padding:1em;margin:1em 0}</style></head>
<body>
<h1>Flask-SocketIO Chat</h1>
<input id="name" placeholder="alice or bob"><button onclick="doLogin()">Login</button>
<div id="app" style="display:none">
  <input id="room" value="general"><button onclick="joinRoom()">Join</button>
  <div id="typing" style="color:#888;font-size:0.85em"></div>
  <div id="log"></div>
  <input id="msg" placeholder="message" oninput="notifyTyping()">
  <button onclick="sendMsg()">Send</button>
  <button onclick="askAI()">Ask AI</button>
</div>
<script>
let socket, currentRoom = 'general';
function doLogin() {
  fetch('/login', {method:'POST', headers:{'Content-Type':'application/json'},
    body: JSON.stringify({name: document.getElementById('name').value})})
    .then(r => r.json())
    .then(r => {
      document.getElementById('app').style.display = 'block';
      socket = io({transports:['websocket'], auth:{token: r.token}});
      socket.on('ready', d => console.log('ready', d));
      socket.on('chat', m => addMsg(`${m.user}: ${m.text}`));
      socket.on('system', m => addMsg(`[${m.type}] ${m.user || ''} ${m.room}`));
      socket.on('typing', d => {
        document.getElementById('typing').textContent =
          d.users.length ? `${d.users.length} typing...` : '';
      });
      socket.on('history', msgs => msgs.forEach(m => addMsg(`${m.user}: ${m.text}`)));
    });
}
function joinRoom() {
  currentRoom = document.getElementById('room').value;
  socket.emit('join', {room: currentRoom});
}
function sendMsg() {
  const el = document.getElementById('msg');
  socket.emit('chat', {room: currentRoom, text: el.value});
  el.value = '';
}
function notifyTyping() {
  socket.emit('typing', {room: currentRoom});
}
function askAI() {
  socket.emit('ask_ai', {room: currentRoom});
}
function addMsg(t) {
  const log = document.getElementById('log');
  log.innerHTML += `<div>${t}</div>`;
  log.scrollTop = log.scrollHeight;
}
</script></body></html>
"""

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
```

### Try it

```bash
pip install flask flask-socketio flask-login
python chat.py
# Open two browser windows at http://localhost:5000
# Log in as 'alice' in one, 'bob' in the other
# Join room 'general' in both, send messages
# Click "Ask AI" — a fake background emit arrives 2s later
```

### Production deployment

#### gunicorn + eventlet (recommended)

```bash
pip install gunicorn eventlet

# -k eventlet: use eventlet worker class
# --workers 4: number of processes (each holds thousands of sockets)
# --worker-connections 1000: greenlets per worker
gunicorn -k eventlet --workers 4 --worker-connections 1000 \
         -b 0.0.0.0:8000 myapp:create_app\(\)
```

#### Nginx WebSocket proxy

```nginx
upstream socketio_backend {
    ip_hash;                      # sticky sessions — critical for WS
    server app1:8000;
    server app2:8000;
}

server {
    listen 443 ssl http2;
    server_name app.example.com;

    location /socket.io/ {
        proxy_pass http://socketio_backend/socket.io/;
        proxy_http_version 1.1;
        proxy_buffering off;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 60s;     # > ping_interval + ping_timeout
        proxy_send_timeout 60s;
    }

    location / {
        proxy_pass http://socketio_backend/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### Docker Compose (multi-worker + Redis message queue)

```yaml
version: "3.9"
services:
  redis:
    image: redis:7-alpine

  web:
    build: .
    command: gunicorn -k eventlet --workers 4 --worker-connections 1000
             -b 0.0.0.0:8000 "chat:create_app()"
    environment:
      SOCKETIO_MQ: redis://redis:6379/3
      SECRET_KEY: changeme
    depends_on: [redis]
    ports: ["8000:8000"]

  nginx:
    image: nginx:1.27-alpine
    volumes: ["./nginx.conf:/etc/nginx/conf.d/default.conf:ro"]
    ports: ["80:80", "443:443"]
    depends_on: [web]
```

### Scaling checklist

- [ ] Eventlet/gevent async mode (not threading)
- [ ] `message_queue` set to Redis or RabbitMQ
- [ ] Sticky sessions at the load balancer
- [ ] Nginx `proxy_read_timeout > ping_interval + ping_timeout`
- [ ] `Upgrade` and `Connection` headers forwarded
- [ ] `transports: ["websocket"]` on client (no silent fallback)
- [ ] Auth on every (re)connect — not session-cookie-only
- [ ] Per-user room (not per-tab) for multi-tab delivery
- [ ] Presence stored in Redis, not in-process dict
- [ ] Sentry SDK with Socket.IO integration
- [ ] Health check: HTTP route returning count of connected sockets
- [ ] Alert: connection count anomaly, error rate, message latency p99
- [ ] Rate-limit incoming events per sid
- [ ] `max_http_buffer_size` capped to protocol's realistic max

---

## 12. References

### Official

- **Flask-SocketIO docs** — https://flask-socketio.readthedocs.io
- **python-socketio docs** — https://python-socketio.readthedocs.io
- **python-engineio docs** — https://python-engineio.readthedocs.io
- **Socket.IO protocol spec** — https://socket.io/docs/v4/
- **Browser client API** — https://socket.io/docs/v4/client-api/
- **GitHub** — https://github.com/miguelgrinberg/Flask-SocketIO

### WebSocket fundamentals

- RFC 6455 — https://www.rfc-editor.org/rfc/rfc6455
- MDN: Writing WebSocket servers — https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API/Writing_WebSocket_servers
- HTML Living Standard, WebSocket section — https://html.spec.whatwg.org/multipage/web-sockets.html

### Async backends

- Eventlet — https://eventlet.net
- Gevent — https://www.gevent.org
- gevent-websocket — https://www.gelens.nl/code/gevent-websocket/
- Uvicorn (ASGI) — https://www.uvicorn.org

### Deployment

- **gunicorn + eventlet guide** — https://docs.gunicorn.org/en/stable/design.html#sync-vs-async-workers
- **Nginx WebSocket proxying** — https://nginx.org/en/docs/http/websocket.html
- **HAProxy WebSocket load balancing** — https://www.haproxy.com/blog/haproxy-and-websockets

### Tutorials & deep dives

- Miguel Grinberg's "Flask-SocketIO" — https://blog.miguelgrinberg.com/post/easy-websockets-with-flask-gevent
- "Scaling Socket.IO to multiple nodes" — https://socket.io/docs/v4/using-multiple-nodes/
- "How Socket.IO works" — https://socket.io/docs/v4/how-it-works/

### Cross-vault wikilinks

- [[Celery]] — pushing real-time progress from background tasks
- [[Flask-Login]] — `current_user` inside socket handlers
- [[Flask-JWT-Extended]] — token-based WebSocket auth
- [[Flask-CORS]] — same-origin policy and CORS background
- [[Flask-Caching]] — caching handler inputs
- [[Flask-Limiter]] — rate-limiting incoming events
- [[Marshmallow]] — validating event payloads
- [[Project-Structure]] — where `socketio.init_app` and `events.py` live
- [[Security-Best-Practices]] — auth on every reconnect, rate limits, payload validation
- [[Performance-Optimization]] — async mode choice, sticky sessions, message queue

---

> [!quote] Final metaphor
> Flask-SocketIO is the **open channel** behind your Flask app. Where normal HTTP makes the client dial in for every word, WebSockets keep the line open — and Flask-SocketIO gives you the protocol (events, rooms, namespaces, acks) to make that line useful. Pair it with [[Celery]] for non-blocking background work, with [[Flask-Login]] or [[Flask-JWT-Extended]] for identity, and with a Redis message queue for multi-worker scaling. Do that, and your Flask app graduates from "request-response website" to "real-time application" without leaving the Pallets ecosystem.
