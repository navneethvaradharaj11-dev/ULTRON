import pytest
from app.knowledge.knowledge_engine import KnowledgeEngine
from app.database.repositories.knowledge_repo import KnowledgeRepository


@pytest.mark.asyncio
async def test_full_multimodal_knowledge_pipeline_e2e(db_session):
    engine = KnowledgeEngine(db_session)
    user_id = "user_phase8_e2e"

    # 1. Create Workspace
    ws_res = await engine.create_workspace(user_id=user_id, name="OS Research Workspace", description="CPU & OS Notes")
    ws_id = ws_res["workspace_id"]
    assert ws_id is not None

    # 2. Upload & Ingest Multimodal Sources
    # Source A: Text / Document Notes
    text_bytes = b"CPU Scheduling algorithms include First-Come First-Served and Round Robin scheduling."
    res_a = await engine.upload_and_ingest_source(
        user_id=user_id,
        workspace_id=ws_id,
        filename="scheduling_notes.txt",
        content_bytes=text_bytes,
        mime_type="text/plain"
    )
    assert res_a["status"] == "COMPLETED"
    assert res_a["chunks_created"] >= 1

    # Source B: Spreadsheet CSV Data
    csv_bytes = b"Process,Priority,BurstTime\nP1,1,10\nP2,2,5\nP3,3,8"
    res_b = await engine.upload_and_ingest_source(
        user_id=user_id,
        workspace_id=ws_id,
        filename="processes.csv",
        content_bytes=csv_bytes,
        mime_type="text/csv"
    )
    assert res_b["status"] == "COMPLETED"

    # 3. Content Hash Deduplication
    res_dup = await engine.upload_and_ingest_source(
        user_id=user_id,
        workspace_id=ws_id,
        filename="scheduling_notes.txt",
        content_bytes=text_bytes,
        mime_type="text/plain"
    )
    assert res_dup["deduplicated"] is True

    # 4. Perform Hybrid Search & Traceable Citation Verification
    search_res = await engine.query_knowledge(
        user_id=user_id,
        query="Round Robin scheduling algorithms",
        workspace_id=ws_id,
        top_k=5
    )
    assert len(search_res["results"]) >= 1
    assert len(search_res["citations"]) >= 1
    assert "[1] scheduling_notes.txt" in search_res["citations"][0]

    # 5. Knowledge Graph Verification
    graph = await engine.get_workspace_graph(user_id, ws_id)
    assert graph["workspace_id"] == ws_id

    # 6. Multi-Tenant Isolation (User B should receive 0 results for User A's workspace)
    other_user = "user_phase8_unauthorized"
    other_search = await engine.query_knowledge(
        user_id=other_user,
        query="Round Robin scheduling algorithms",
        workspace_id=ws_id,
        top_k=5
    )
    assert len(other_search["results"]) == 0

    # 7. Clean Up Source Deletion
    del_success = await engine.delete_source(res_a["source_id"], user_id)
    assert del_success is True
