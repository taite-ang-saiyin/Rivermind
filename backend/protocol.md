# Texas Hold'em WebSocket Protocol

This document describes the minimal JSON contracts used between client and server.

## Client -> Server (MOVE)

Actions are sent as a single `MOVE` message. The `amount` field is only valid for
`raise`.

Example call:

```json
{
  "type": "MOVE",
  "action": "call"
}
```

Example raise:

```json
{
  "type": "MOVE",
  "action": "raise",
  "amount": 120
}
```

## Server -> Client (STATE)

The server sends the full public state. The `hand` field is only included for
the human player's own view.

```json
{
  "type": "STATE",
  "payload": {
    "session_id": "1b1f7e6d8a2b4b6a9f7b6e3b6a9f7b6e",
    "street": "flop",
    "pot": 150,
    "community_cards": ["Ah", "Td", "7s"],
    "hand": ["Kc", "Kh"],
    "stacks": {
      "p1": 850,
      "p2": 1000
    },
    "bets": {
      "p1": 50,
      "p2": 50
    },
    "current_player": "p2",
    "legal_actions": ["check", "raise", "fold"],
    "action_history": [
      {
        "player_id": "p1",
        "action": {
          "action": "raise",
          "amount": 50
        }
      }
    ]
  }
}
```

## Server -> Client (EVENT)

Event messages are optional and intended for UI animation timing.

```json
{
  "type": "EVENT",
  "payload": {
    "event": "DEAL_FLOP",
    "data": {
      "cards": ["Ah", "Td", "7s"]
    }
  }
}
```

## Server -> Client (ERROR)

Validation errors should be returned as human-readable messages.

```json
{
  "type": "ERROR",
  "payload": {
    "message": "Invalid message",
    "details": [
      "amount: amount is required for raise"
    ]
  }
}
```
