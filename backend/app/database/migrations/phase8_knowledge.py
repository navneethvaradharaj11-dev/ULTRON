import logging
from sqlalchemy import text
from app.database.connection import engine

logger = logging.getLogger(__name__)

PHASE8_TABLES_SQL = [
    """
    CREATE TABLE IF NOT EXISTS knowledge_workspaces (
        id VARCHAR(36) PRIMARY KEY,
        user_id VARCHAR(36) NOT NULL,
        name VARCHAR(255) NOT NULL,
        description TEXT NULL,
        settings_json JSON NULL,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        INDEX idx_k_workspaces_user_id (user_id)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS knowledge_sources (
        id VARCHAR(36) PRIMARY KEY,
        user_id VARCHAR(36) NOT NULL,
        workspace_id VARCHAR(36) NOT NULL,
        source_type VARCHAR(64) NOT NULL,
        filename VARCHAR(255) NOT NULL,
        mime_type VARCHAR(128) NOT NULL,
        size_bytes INT NOT NULL DEFAULT 0,
        content_hash VARCHAR(64) NOT NULL,
        origin VARCHAR(255) NOT NULL,
        status VARCHAR(32) NOT NULL DEFAULT 'PENDING',
        metadata_json JSON NULL,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        INDEX idx_k_sources_user_ws (user_id, workspace_id),
        INDEX idx_k_sources_hash (content_hash)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS knowledge_documents (
        id VARCHAR(36) PRIMARY KEY,
        source_id VARCHAR(36) NOT NULL,
        user_id VARCHAR(36) NOT NULL,
        title VARCHAR(255) NOT NULL,
        page_count INT NOT NULL DEFAULT 1,
        language VARCHAR(32) NULL,
        summary TEXT NULL,
        metadata_json JSON NULL,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_k_docs_source (source_id),
        INDEX idx_k_docs_user (user_id)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS knowledge_chunks (
        id VARCHAR(36) PRIMARY KEY,
        source_id VARCHAR(36) NOT NULL,
        user_id VARCHAR(36) NOT NULL,
        sequence INT NOT NULL,
        content TEXT NOT NULL,
        token_count INT NOT NULL DEFAULT 0,
        location_json JSON NULL,
        checksum VARCHAR(64) NOT NULL,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_k_chunks_source (source_id),
        INDEX idx_k_chunks_user (user_id)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS knowledge_embeddings (
        id VARCHAR(36) PRIMARY KEY,
        chunk_id VARCHAR(36) NOT NULL,
        source_id VARCHAR(36) NOT NULL,
        user_id VARCHAR(36) NOT NULL,
        provider_name VARCHAR(64) NOT NULL,
        model_name VARCHAR(64) NOT NULL,
        dimension INT NOT NULL,
        vector_json JSON NOT NULL,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_k_embed_chunk (chunk_id),
        INDEX idx_k_embed_user (user_id)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS knowledge_entities (
        id VARCHAR(36) PRIMARY KEY,
        user_id VARCHAR(36) NOT NULL,
        workspace_id VARCHAR(36) NOT NULL,
        name VARCHAR(255) NOT NULL,
        entity_type VARCHAR(64) NOT NULL,
        confidence FLOAT NOT NULL DEFAULT 1.0,
        evidence_json JSON NULL,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_k_entities_user_ws (user_id, workspace_id),
        INDEX idx_k_entities_name (name)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS knowledge_relationships (
        id VARCHAR(36) PRIMARY KEY,
        user_id VARCHAR(36) NOT NULL,
        workspace_id VARCHAR(36) NOT NULL,
        source_entity_id VARCHAR(36) NOT NULL,
        target_entity_id VARCHAR(36) NOT NULL,
        relation_type VARCHAR(64) NOT NULL,
        provenance TEXT NOT NULL,
        confidence FLOAT NOT NULL DEFAULT 1.0,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_k_rel_user_ws (user_id, workspace_id)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS knowledge_citations (
        id VARCHAR(36) PRIMARY KEY,
        source_id VARCHAR(36) NOT NULL,
        user_id VARCHAR(36) NOT NULL,
        citation_text TEXT NOT NULL,
        location_spec VARCHAR(255) NOT NULL,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_k_citations_source (source_id),
        INDEX idx_k_citations_user (user_id)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS knowledge_collections (
        id VARCHAR(36) PRIMARY KEY,
        user_id VARCHAR(36) NOT NULL,
        workspace_id VARCHAR(36) NOT NULL,
        name VARCHAR(255) NOT NULL,
        description TEXT NULL,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_k_coll_user_ws (user_id, workspace_id)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS knowledge_jobs (
        id VARCHAR(36) PRIMARY KEY,
        user_id VARCHAR(36) NOT NULL,
        source_id VARCHAR(36) NOT NULL,
        job_type VARCHAR(64) NOT NULL,
        status VARCHAR(32) NOT NULL DEFAULT 'PENDING',
        error_message TEXT NULL,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        completed_at DATETIME NULL,
        INDEX idx_k_jobs_user (user_id),
        INDEX idx_k_jobs_source (source_id)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS knowledge_artifacts (
        id VARCHAR(36) PRIMARY KEY,
        user_id VARCHAR(36) NOT NULL,
        source_id VARCHAR(36) NOT NULL,
        filename VARCHAR(255) NOT NULL,
        file_path TEXT NOT NULL,
        artifact_type VARCHAR(64) NOT NULL,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_k_arts_user (user_id),
        INDEX idx_k_arts_source (source_id)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS knowledge_access_logs (
        id VARCHAR(36) PRIMARY KEY,
        user_id VARCHAR(36) NOT NULL,
        source_id VARCHAR(36) NOT NULL,
        action VARCHAR(64) NOT NULL,
        timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_k_logs_user (user_id),
        INDEX idx_k_logs_source (source_id)
    );
    """
]

async def run_phase8_migrations():
    """Execute DDL migrations for Phase 8 Multimodal Knowledge Fabric."""
    logger.info("Executing Phase 8 Multimodal Knowledge Fabric DDL migrations...")
    try:
        async with engine.begin() as conn:
            for sql_stmt in PHASE8_TABLES_SQL:
                try:
                    await conn.execute(text(sql_stmt))
                    # commit handled by async with
                except Exception as e:
                    logger.warning("Phase 8 Migration stmt notice: %s", e)
    except Exception as e:
        logger.warning("Phase 8 Migration notice: %s", e)

