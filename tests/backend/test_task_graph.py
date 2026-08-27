import pytest
from app.engine.task_graph import TaskGraph, TaskNode
from app.engine.contracts import TaskStatus


def test_task_graph_dependency_resolution():
    graph = TaskGraph("exec_1", "Research AI trends and generate code")

    t1 = TaskNode("task_1", "Research latest AI trends", assigned_agent="researcher")
    t2 = TaskNode("task_2", "Generate code report", assigned_agent="coder", dependencies=["task_1"])
    t3 = TaskNode("task_3", "Review report", assigned_agent="reviewer", dependencies=["task_2"])

    graph.add_task(t1)
    graph.add_task(t2)
    graph.add_task(t3)

    assert graph.validate_dag() is True

    # Initially only task_1 is ready
    executable = graph.get_executable_tasks()
    assert len(executable) == 1
    assert executable[0].id == "task_1"

    # Mark task_1 completed
    t1.status = TaskStatus.COMPLETED

    # Now task_2 should be ready
    executable_step2 = graph.get_executable_tasks()
    assert len(executable_step2) == 1
    assert executable_step2[0].id == "task_2"


def test_task_graph_cancellation():
    graph = TaskGraph("exec_2", "Sample goal")
    t1 = TaskNode("task_1", "Step 1", assigned_agent="coder")
    t2 = TaskNode("task_2", "Step 2", assigned_agent="reviewer", dependencies=["task_1"])
    graph.add_task(t1)
    graph.add_task(t2)

    graph.cancel_all()
    assert t1.status == TaskStatus.CANCELLED
    assert t2.status == TaskStatus.CANCELLED
    assert graph.is_failed() is True
