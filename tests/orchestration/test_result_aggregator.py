from app.orchestration.result_aggregator import ResultAggregator

def test_result_aggregator_synthesis():
    tasks_res = [
        {"task_id": "t1", "agent": "researcher", "status": "COMPLETED"},
        {"task_id": "t2", "agent": "coder", "status": "COMPLETED"}
    ]

    res = ResultAggregator.aggregate_results(
        workflow_id="wf_123",
        goal="Build API",
        tasks_results=tasks_res
    )

    assert res.status == "COMPLETED"
    assert res.confidence == 1.0
    assert res.tasks_completed == 2
    assert res.tasks_failed == 0
    assert "sk_live_" not in res.summary
