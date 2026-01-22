from fastapi.testclient import TestClient

from backend.main import app


def test_websocket_initial_state_and_move_val() -> None:
    client = TestClient(app)
    with client.websocket_connect("/ws") as websocket:
        initial = websocket.receive_json()
        assert initial["type"] == "STATE"
        assert "session_id" in initial["payload"]

        websocket.send_json({"type": "MOVE", "val": "call"})
        response = websocket.receive_json()
        assert response["type"] == "STATE"


def test_websocket_malformed_json_returns_error_and_continues() -> None:
    client = TestClient(app)
    with client.websocket_connect("/ws") as websocket:
        websocket.receive_json()

        websocket.send_text("{bad json")
        error = websocket.receive_json()
        assert error["type"] == "ERROR"

        websocket.send_json({"type": "MOVE", "val": "check"})
        response = websocket.receive_json()
        assert response["type"] == "STATE"
