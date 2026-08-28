# Phase 6 Database Schema Specification

## Phase 6 Tables
1. `memory_embeddings`: Vector storage (`vector_json`, `dimension`, `provider_name`)
2. `memory_links`: Related memory edges (`source_memory_id`, `target_memory_id`, `link_type`, `strength`)
3. `memory_versions`: Audit history (`version`, `content`, `importance`, `confidence`, `reason`)
4. `episodic_memories`: Experience records (`goal`, `plan_json`, `agents_used_json`, `lessons_json`)
5. `semantic_memories`: Concept facts (`topic`, `concept`, `facts_json`, `confidence`)
6. `procedural_memories`: Workflows (`workflow_name`, `steps_json`, `success_rate`, `sample_count`)
7. `preference_memories`: Explicit preferences (`key`, `value`, `confidence`, `source`)
8. `learning_events`: Pattern logs (`event_type`, `observation_json`, `pattern_detected`)
9. `strategy_library`: Workflows (`goal_type`, `steps_json`, `success_rate`, `confidence`)
10. `strategy_results`: Execution outcomes (`strategy_id`, `execution_id`, `success`, `duration_ms`)
11. `agent_metrics`: Agent stats (`agent_name`, `total_runs`, `success_rate`, `average_duration_ms`)
12. `execution_feedback`: User ratings (`execution_id`, `rating`, `feedback_text`)
