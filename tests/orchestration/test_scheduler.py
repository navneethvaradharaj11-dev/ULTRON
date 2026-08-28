from app.engine.task_graph import TaskGraph, TaskNode
from app.orchestration.task_scheduler import TaskScheduler

def test_task_scheduler_parallel_group_resolution():
    graph = TaskGraph("exec_1", "Test parallel graph")
    t1 = TaskNode("t1", "Research A", "researcher")
    t2 = TaskNode("t2", "Research B", "researcher")
    t3 = TaskNode("t3", "Synthesize", "reviewer", dependencies=["t1", "t2"])

    graph.add_task(t1)
    graph.add_task(t2)
    graph.add_task(t3)

    scheduler = TaskScheduler(graph)
    
    # Initially t1 and t2 are ready
    ready = scheduler.get_ready_tasks(set(), set())
    ready_ids = [r.task_id for r in ready]
    assert "t1" in ready_ids
    assert "t2" in ready_ids
    assert "t3" not in ready_ids

    # After t1 and t2 complete, t3 becomes ready
    ready_after = scheduler.get_ready_tasks({"t1", "t2"}, set())
    assert len(ready_after) == 1
    assert ready_after[0].task_id == "t3"
