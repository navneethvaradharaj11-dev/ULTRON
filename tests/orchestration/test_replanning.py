from app.engine.task_graph import TaskGraph, TaskNode
from app.orchestration.replanning_engine import ReplanningEngine

def test_replanning_engine():
    graph = TaskGraph("exec_1", "Goal")
    t1 = TaskNode("t1", "Task 1", "researcher")
    t2 = TaskNode("t2", "Task 2", "coder", dependencies=["t1"])
    graph.add_task(t1)
    graph.add_task(t2)

    replanner = ReplanningEngine(max_replans=3)
    new_graph = replanner.replan_graph(graph, "t1", "Source unavailable", 0)

    assert "fallback_t1" in new_graph.nodes
    assert "fallback_t1" in new_graph.nodes["t2"].dependencies
