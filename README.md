# Texas Hold'em Backend

## Run the server

```bash
uvicorn backend.main:app --reload
```

## Manual WebSocket test

Using a WebSocket client such as `websocat`:

```bash
websocat ws://127.0.0.1:8000/ws
```

On connect, you should receive a `STATE` message. Send a MOVE:

```json
{"type":"MOVE","val":"call"}
```

The server should respond with another `STATE` message. The canonical field name
is `action`, but the server also accepts `val` for compatibility.
