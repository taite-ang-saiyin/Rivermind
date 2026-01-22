import json
import logging
from typing import Any, Dict

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.encoders import jsonable_encoder
from pydantic import ValidationError

from .logging_setup import configure_logging
from .schemas import (
    Action,
    ClientMessage,
    ErrorMessage,
    ServerMessage,
    format_validation_error,
)
from .session_store import SessionStore


configure_logging()
logger = logging.getLogger("backend.websocket")

app = FastAPI()
store = SessionStore()


async def send_server_message(websocket: WebSocket, message: ServerMessage) -> None:
    await websocket.send_json(jsonable_encoder(message))


def _parse_json_payload(raw_text: str) -> Dict[str, Any]:
    payload = json.loads(raw_text)
    if not isinstance(payload, dict):
        raise ValueError("Message must be a JSON object")
    return payload


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    await websocket.accept()

    session_id = websocket.query_params.get("session_id")
    session, created = store.get_or_create(session_id)
    logger.info(
        "WebSocket connected session_id=%s created=%s",
        session.session_id,
        created,
    )

    await send_server_message(
        websocket,
        ServerMessage(type="STATE", payload=session.state),
    )

    try:
        while True:
            raw_text = await websocket.receive_text()
            try:
                payload = _parse_json_payload(raw_text)
            except (json.JSONDecodeError, ValueError) as exc:
                await send_server_message(
                    websocket,
                    ServerMessage(
                        type="ERROR",
                        payload=ErrorMessage(message="Invalid JSON", details=[str(exc)]),
                    ),
                )
                continue

            try:
                client_message = ClientMessage.parse_obj(payload)
            except ValidationError as exc:
                await send_server_message(
                    websocket,
                    ServerMessage(
                        type="ERROR",
                        payload=format_validation_error(exc),
                    ),
                )
                continue

            action = Action(action=client_message.action, amount=client_message.amount)
            updated_state = store.record_action(session.session_id, action)

            await send_server_message(
                websocket,
                ServerMessage(type="STATE", payload=updated_state),
            )
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected session_id=%s", session.session_id)
    except Exception:
        logger.exception("WebSocket error session_id=%s", session.session_id)
