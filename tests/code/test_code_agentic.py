import pytest
from app.ai.model_manager import ModelManager
from app.agents.code_agent import CodeAgent
from app.sandbox.sandbox_manager import SandboxManager


@pytest.mark.asyncio
async def test_agentic_1_python_factorial():
    agent = CodeAgent(ModelManager())
    res = await agent.execute_action(
        action_dict={
            "action": "CREATE_FILE",
            "path": "factorial.py",
            "content": "import math\ndef fact(n):\n    return math.factorial(n)\nprint(fact(5))\n",
            "language": "python"
        },
        execution_id="ag_1", task_id="t1", user_id="u1"
    )
    assert res["status"] == "COMPLETED"

    exec_res = await agent.execute_action(
        action_dict={
            "action": "EXECUTE",
            "language": "python",
            "entrypoint": "factorial.py"
        },
        execution_id="ag_1", task_id="t1", user_id="u1"
    )
    assert exec_res["status"] == "COMPLETED"
    assert "120" in exec_res["stdout"]


@pytest.mark.asyncio
async def test_agentic_2_c_linked_list():
    agent = CodeAgent(ModelManager())
    c_code = """
#include <stdio.h>
#include <stdlib.h>
struct Node { int data; struct Node* next; };
int main() {
    struct Node* head = (struct Node*)malloc(sizeof(struct Node));
    head->data = 42; head->next = NULL;
    printf("Node data: %d\\n", head->data);
    free(head);
    return 0;
}
"""
    await agent.execute_action(
        action_dict={"action": "CREATE_FILE", "path": "ll.c", "content": c_code, "language": "c"},
        execution_id="ag_2", task_id="t2", user_id="u1"
    )

    comp_res = await agent.execute_action(
        action_dict={"action": "COMPILE", "language": "c", "entrypoint": "ll.c"},
        execution_id="ag_2", task_id="t2", user_id="u1"
    )
    if comp_res["status"] == "COMPLETED":
        run_res = await agent.execute_action(
            action_dict={"action": "EXECUTE", "language": "c", "entrypoint": "ll.c"},
            execution_id="ag_2", task_id="t2", user_id="u1"
        )
        assert run_res["status"] == "COMPLETED"
        assert "Node data: 42" in run_res["stdout"]


@pytest.mark.asyncio
async def test_agentic_3_cpp_array_sort():
    agent = CodeAgent(ModelManager())
    cpp_code = """
#include <iostream>
#include <vector>
#include <algorithm>
int main() {
    std::vector<int> arr = {5, 2, 8, 1, 3};
    std::sort(arr.begin(), arr.end());
    for(int n : arr) std::cout << n << " ";
    std::cout << "\\n";
    return 0;
}
"""
    await agent.execute_action(
        action_dict={"action": "CREATE_FILE", "path": "sort.cpp", "content": cpp_code, "language": "cpp"},
        execution_id="ag_3", task_id="t3", user_id="u1"
    )

    comp_res = await agent.execute_action(
        action_dict={"action": "COMPILE", "language": "cpp", "entrypoint": "sort.cpp"},
        execution_id="ag_3", task_id="t3", user_id="u1"
    )
    if comp_res["status"] == "COMPLETED":
        run_res = await agent.execute_action(
            action_dict={"action": "EXECUTE", "language": "cpp", "entrypoint": "sort.cpp"},
            execution_id="ag_3", task_id="t3", user_id="u1"
        )
        assert run_res["status"] == "COMPLETED"
        assert "1 2 3 5 8" in run_res["stdout"]


@pytest.mark.asyncio
async def test_agentic_4_js_array_analysis():
    agent = CodeAgent(ModelManager())
    js_code = "const nums = [10, 20, 30]; const sum = nums.reduce((a, b) => a + b, 0); console.log('SUM:' + sum);"
    await agent.execute_action(
        action_dict={"action": "CREATE_FILE", "path": "analyze.js", "content": js_code, "language": "javascript"},
        execution_id="ag_4", task_id="t4", user_id="u1"
    )

    run_res = await agent.execute_action(
        action_dict={"action": "EXECUTE", "language": "javascript", "entrypoint": "analyze.js"},
        execution_id="ag_4", task_id="t4", user_id="u1"
    )
    assert run_res["status"] == "COMPLETED"
    assert "SUM:60" in run_res["stdout"]


@pytest.mark.asyncio
async def test_agentic_5_self_debugging():
    agent = CodeAgent(ModelManager())
    # Broken python syntax
    await agent.execute_action(
        action_dict={"action": "CREATE_FILE", "path": "broken.py", "content": "print('hello", "language": "python"},
        execution_id="ag_5", task_id="t5", user_id="u1"
    )

    res = await agent.execute_action(
        action_dict={"action": "EXECUTE", "language": "python", "entrypoint": "broken.py"},
        execution_id="ag_5", task_id="t5", user_id="u1"
    )
    assert res["status"] in ("FAILED", "RUNTIME_ERROR")

    # Fix
    await agent.execute_action(
        action_dict={"action": "UPDATE_FILE", "path": "broken.py", "content": "print('hello')", "language": "python"},
        execution_id="ag_5", task_id="t5", user_id="u1"
    )

    res_fixed = await agent.execute_action(
        action_dict={"action": "EXECUTE", "language": "python", "entrypoint": "broken.py"},
        execution_id="ag_5", task_id="t5", user_id="u1"
    )
    assert res_fixed["status"] == "COMPLETED"
    assert "hello" in res_fixed["stdout"]


@pytest.mark.asyncio
async def test_agentic_6_compile_failure_recovery():
    agent = CodeAgent(ModelManager())
    # Broken C code
    await agent.execute_action(
        action_dict={"action": "CREATE_FILE", "path": "bad.c", "content": "int main() { return ", "language": "c"},
        execution_id="ag_6", task_id="t6", user_id="u1"
    )

    comp_res = await agent.execute_action(
        action_dict={"action": "COMPILE", "language": "c", "entrypoint": "bad.c"},
        execution_id="ag_6", task_id="t6", user_id="u1"
    )
    assert comp_res["status"] == "COMPILE_ERROR"

    # Fix code
    await agent.execute_action(
        action_dict={"action": "UPDATE_FILE", "path": "bad.c", "content": "int main() { return 0; }", "language": "c"},
        execution_id="ag_6", task_id="t6", user_id="u1"
    )

    from app.sandbox.runtime import CRuntime
    comp_fixed = await agent.execute_action(
        action_dict={"action": "COMPILE", "language": "c", "entrypoint": "bad.c"},
        execution_id="ag_6", task_id="t6", user_id="u1"
    )
    if CRuntime().is_available():
        assert comp_fixed["status"] == "COMPLETED"
    else:
        assert comp_fixed["status"] == "COMPILE_ERROR"
        assert "RUNTIME_UNAVAILABLE" in comp_fixed["stderr"]



@pytest.mark.asyncio
async def test_agentic_7_infinite_loop_timeout():
    agent = CodeAgent(ModelManager())
    await agent.execute_action(
        action_dict={"action": "CREATE_FILE", "path": "loop.py", "content": "while True: pass", "language": "python"},
        execution_id="ag_7", task_id="t7", user_id="u1"
    )

    res = await agent.execute_action(
        action_dict={"action": "EXECUTE", "language": "python", "entrypoint": "loop.py"},
        execution_id="ag_7", task_id="t7", user_id="u1"
    )
    assert res["status"] == "TIMEOUT"


@pytest.mark.asyncio
async def test_agentic_8_network_attempt_denied():
    from app.sandbox.network_policy import NetworkPolicy, NetworkPolicyMode
    np = NetworkPolicy(mode=NetworkPolicyMode.DENY_ALL)
    allowed, reason = np.validate_destination("https://example.com")
    assert not allowed
    assert "NETWORK_DENIED" in reason


@pytest.mark.asyncio
async def test_agentic_9_host_filesystem_attempt_denied():
    agent = CodeAgent(ModelManager())
    res = await agent.execute_action(
        action_dict={"action": "READ_FILE", "path": "../../.env"},
        execution_id="ag_9", task_id="t9", user_id="u1"
    )
    assert res["status"] == "ACCESS_DENIED"


@pytest.mark.asyncio
async def test_agentic_10_cross_user_access_denied():
    sm = SandboxManager()
    sm.get_or_create_session(execution_id="ex_user_1", task_id="t10", user_id="user_A")
    with pytest.raises(PermissionError, match="ACCESS_DENIED"):
        sm.get_session(execution_id="ex_user_1", task_id="t10", user_id="user_B")
