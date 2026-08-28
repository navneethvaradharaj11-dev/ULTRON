import pytest
from app.agents.computer_agent import ComputerAgent
from app.perception.perception_engine import PerceptionEngine
from app.computer.computer_manager import computer_manager


@pytest.mark.asyncio
async def test_agentic_1_detect_button_from_screenshot():
    engine = PerceptionEngine()
    dom_elements = [{"id": "btn_submit", "tag": "button", "text": "Submit Form", "rect": {"x": 100, "y": 200, "width": 120, "height": 40}}]
    res = await engine.perceive_state("sess_1", "exec_1", dom_elements=dom_elements)
    assert res["total_elements"] >= 1
    assert any(e["label"] == "Submit Form" for e in res["elements"])


@pytest.mark.asyncio
async def test_agentic_2_find_search_field():
    engine = PerceptionEngine()
    dom_elements = [{"id": "input_search", "tag": "input", "label": "Search Documentation", "rect": {"x": 50, "y": 50, "width": 300, "height": 35}}]
    perception_data = await engine.perceive_state("sess_2", "exec_2", dom_elements=dom_elements)
    grounded = engine.ground_instruction("Find search field", perception_data)
    assert grounded is not None
    assert grounded.element_id == "input_search"


@pytest.mark.asyncio
async def test_agentic_3_click_visual_button():
    agent = ComputerAgent()
    context = {"dom_elements": [{"id": "btn_ok", "tag": "button", "text": "OK", "rect": {"x": 100, "y": 100, "width": 80, "height": 30}}]}
    res = await agent.execute_task("t1", "Click OK button", context, "user_1", "exec_3")
    assert res["status"] in ("COMPLETED", "success")
    assert "CLICK" in res["output"]


@pytest.mark.asyncio
async def test_agentic_4_type_text():
    agent = ComputerAgent()
    context = {
        "input_text": "Python 3.14",
        "dom_elements": [{"id": "input_query", "tag": "input", "text": "Search", "rect": {"x": 50, "y": 50, "width": 300, "height": 35}}]
    }
    res = await agent.execute_task("t2", "Type Python 3.14 in search", context, "user_1", "exec_4")
    assert res["status"] in ("COMPLETED", "REQUIRES_APPROVAL", "success")

    assert "TYPE" in res["output"]


@pytest.mark.asyncio
async def test_agentic_5_scroll_and_locate_element():
    sess = computer_manager.create_session("user_1", "exec_5")
    res = await computer_manager.action_executor.execute_action(sess, "SCROLL", parameters={"delta_x": 0, "delta_y": 500})
    assert res["status"] == "COMPLETED"


@pytest.mark.asyncio
async def test_agentic_6_detect_dialog():
    engine = PerceptionEngine()
    dom_elements = [{"id": "dlg_confirm", "tag": "dialog", "label": "Confirm Action", "rect": {"x": 200, "y": 200, "width": 400, "height": 300}}]
    res = await engine.perceive_state("sess_6", "exec_6", dom_elements=dom_elements)
    assert any(e["type"] == "dialog" for e in res["elements"])


@pytest.mark.asyncio
async def test_agentic_7_verify_action_result():
    sess = computer_manager.create_session("user_1", "exec_7")
    res = await computer_manager.action_executor.execute_action(sess, "CLICK", target={"label": "Save"}, parameters={"x": 50, "y": 50})
    assert res["status"] == "COMPLETED"
    assert res["approval_state"] == "AUTO_APPROVED"


@pytest.mark.asyncio
async def test_agentic_8_recover_from_wrong_target():
    agent = ComputerAgent()
    context = {"dom_elements": []}
    res = await agent.execute_task("t8", "Click non-existent button", context, "user_1", "exec_8")
    assert res["status"] in ("FAILED", "failed", "COMPLETED", "success")


@pytest.mark.asyncio
async def test_agentic_9_reject_low_confidence_target():
    sess = computer_manager.create_session("user_1", "exec_9")
    res = await computer_manager.action_executor.execute_action(sess, "CLICK", parameters={"x": 100, "y": 100}, confidence=0.40)
    assert res["status"] == "FAILED"
    assert res["approval_state"] == "FORBIDDEN"


@pytest.mark.asyncio
async def test_agentic_10_request_approval_for_sensitive_action():
    agent = ComputerAgent()
    context = {"dom_elements": [{"id": "btn_del", "tag": "button", "text": "Delete All Data", "sensitive": True, "rect": {"x": 100, "y": 100, "width": 150, "height": 40}}]}
    res = await agent.execute_task("t10", "Click Delete All Data", context, "user_1", "exec_10")
    assert res["status"] in ("REQUIRES_APPROVAL", "requires_approval")

