# WebSocket API

## Connection

```
ws://<host>/ws/messages/?token=<JWT_ACCESS_TOKEN>
```

- Authentication via `token` query parameter (JWT access token).
- Unauthenticated connections are immediately closed.

---

## Server → Client Events

### `ping`

Sent periodically by the server to keep the connection alive.

```json
{ "type": "ping" }
```

**Required response:** Send back a `pong` message (see below). Failing to respond will close the connection.

---

### `new_message`

Pushed when another user sends you a message.

```json
{
  "type": "new_message",
  "message": {
    "id": 42,
    "sender": 3,
    "message": "Hello!",
    "timestamp": "2026-03-30T10:15:00.000000+00:00"
  }
}
```

| Field       | Type   | Description              |
|-------------|--------|--------------------------|
| `id`        | int    | Message ID               |
| `sender`    | int    | Sender's user ID         |
| `message`   | string | Message text             |
| `timestamp` | string | ISO 8601 timestamp (UTC) |

---

### `read_message`

Pushed when the other user reads your messages.

```json
{
  "type": "read_message",
  "message": {
    "last_read_message_id": 42,
    "reader_id": 3
  }
}
```

| Field                  | Type | Description                        |
|------------------------|------|------------------------------------|
| `last_read_message_id` | int  | ID of the most recent read message |
| `reader_id`            | int  | User ID of the person who read     |

---

## Client → Server Events

### `pong`

Must be sent in response to every `ping`.

```json
{ "type": "pong" }
```

> No other client → server messages are handled. Messages are sent via the REST API (`POST /api/v1/conversations/<user_id>/messages/`).
