import pytest
from pydantic import ValidationError

from backend.schemas import (
    Action,
    ActionRecord,
    ActionType,
    ClientMessage,
    EventMessage,
    EventType,
    GameStatePublic,
    ServerMessage,
    Street,
    format_validation_error,
)


def test_client_message_call() -> None:
    message = ClientMessage(type="MOVE", action=ActionType.CALL)
    assert message.amount is None


def test_client_message_val_alias() -> None:
    message = ClientMessage(type="MOVE", val="call")
    assert message.action == ActionType.CALL


def test_client_message_raise_requires_amount() -> None:
    with pytest.raises(ValidationError) as excinfo:
        ClientMessage(type="MOVE", action="raise")

    assert "amount is required for raise" in excinfo.value.errors()[0]["msg"]


def test_client_message_non_raise_rejects_amount() -> None:
    with pytest.raises(ValidationError) as excinfo:
        ClientMessage(type="MOVE", action="check", amount=10)

    assert "amount is only valid for raise" in excinfo.value.errors()[0]["msg"]


def test_server_message_state_round_trip() -> None:
    state = GameStatePublic(
        street=Street.PREFLOP,
        pot=100,
        community_cards=[],
        hand=["As", "Kd"],
        stacks={"p1": 900, "p2": 1000},
        bets={"p1": 50, "p2": 50},
        current_player="p1",
        legal_actions=[ActionType.CALL, ActionType.RAISE, ActionType.FOLD],
        action_history=[
            ActionRecord(
                player_id="p2",
                action=Action(action=ActionType.RAISE, amount=50),
            )
        ],
    )

    message = ServerMessage(type="STATE", payload=state)
    assert message.payload.street == Street.PREFLOP


def test_server_message_payload_type_mismatch() -> None:
    state = GameStatePublic(
        street=Street.FLOP,
        pot=150,
        community_cards=["Ah", "Td", "7s"],
        hand=None,
        stacks={"p1": 850, "p2": 1000},
        bets={"p1": 50, "p2": 50},
        current_player="p2",
        legal_actions=[ActionType.CHECK, ActionType.RAISE, ActionType.FOLD],
        action_history=[],
    )

    with pytest.raises(ValidationError) as excinfo:
        ServerMessage(type="ERROR", payload=state)

    assert "payload must be ErrorMessage for ERROR" in excinfo.value.errors()[0][
        "msg"
    ]


def test_event_message() -> None:
    event = EventMessage(event=EventType.DEAL_FLOP, data={"cards": ["Ah", "Td", "7s"]})
    message = ServerMessage(type="EVENT", payload=event)
    assert message.payload.event == EventType.DEAL_FLOP


def test_format_validation_error() -> None:
    with pytest.raises(ValidationError) as excinfo:
        ClientMessage(type="MOVE", action="raise")

    error_payload = format_validation_error(excinfo.value)
    assert error_payload.message == "Invalid message"
    assert "amount is required for raise" in error_payload.details[0]
