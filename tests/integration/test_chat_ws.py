import pytest
import json
from starlette.testclient import TestClient
from app.main import app
from app.security.authentication import create_access_token


def test_websocket_chat_stream():
    client = TestClient(app)
    
    # 1. Register & Login user to get valid token & conversation
    reg_res = client.post("/api/v1/auth/register", json={
        "username": "ws_user_test",
        "email": "ws_user@test.com",
        "password": "Password123"
    })
    
    login_res = client.post("/api/v1/auth/login", data={
        "username": "ws_user_test",
        "password": "Password123"
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Create conversation
    conv_res = client.post("/api/v1/chat/conversations", json={"title": "WS Test Conv"}, headers=headers)
    conv_id = conv_res.json()["id"]

    # 3. Connect to WebSocket with token
    with client.websocket_connect(f"/ws/chat/{conv_id}?token={token}") as websocket:
        websocket.send_text(json.dumps({"message": "calculate 25 * 4"}))

        event1 = websocket.receive_json()
        assert event1["type"] == "message_start"

        event2 = websocket.receive_json()
        assert event2["type"] == "agent_started"

        event3 = websocket.receive_json()
        assert event3["type"] == "agent_progress"

        event4 = websocket.receive_json()
        assert event4["type"] == "tool_started"
        assert event4["tool_name"] == "calculator"

        event5 = websocket.receive_json()
        assert event5["type"] == "tool_completed"
        assert str(event5["result"]) == "100"
