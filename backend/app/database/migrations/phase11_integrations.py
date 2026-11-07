import logging
from sqlalchemy import text
from app.database.connection import engine

logger = logging.getLogger("ULTRON.Migrations.Phase11")


async def run_phase11_migrations():
    """Idempotent DDL migration script for Phase 11 Universal Integrations & Connector Fabric."""
    statements = [
        """
        CREATE TABLE IF NOT EXISTS integrations (
            id VARCHAR(36) PRIMARY KEY,
            name VARCHAR(64) UNIQUE NOT NULL,
            version VARCHAR(32) NOT NULL DEFAULT '1.0.0',
            provider VARCHAR(64) NOT NULL,
            description TEXT NOT NULL,
            capabilities_json JSON NULL,
            risk_level VARCHAR(32) NOT NULL DEFAULT 'LOW',
            health_status VARCHAR(32) NOT NULL DEFAULT 'CONNECTED',
            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """,
        """
        CREATE TABLE IF NOT EXISTS integration_connections (
            id VARCHAR(36) PRIMARY KEY,
            user_id VARCHAR(36) NOT NULL,
            integration_id VARCHAR(64) NOT NULL,
            status VARCHAR(32) NOT NULL DEFAULT 'CONNECTED',
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_integ_conn_user (user_id),
            INDEX idx_integ_conn_integ (integration_id),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """,
        """
        CREATE TABLE IF NOT EXISTS integration_credentials (
            id VARCHAR(36) PRIMARY KEY,
            user_id VARCHAR(36) NOT NULL,
            integration_id VARCHAR(64) NOT NULL,
            encrypted_access_token TEXT NULL,
            encrypted_refresh_token TEXT NULL,
            encrypted_api_key TEXT NULL,
            expires_at DATETIME NULL,
            scopes_json JSON NULL,
            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_integ_cred_user (user_id),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """,
        """
        CREATE TABLE IF NOT EXISTS integration_audit_logs (
            id VARCHAR(36) PRIMARY KEY,
            user_id VARCHAR(36) NOT NULL,
            integration_id VARCHAR(64) NOT NULL,
            operation_id VARCHAR(64) NOT NULL,
            status VARCHAR(32) NOT NULL,
            duration_ms INT NOT NULL DEFAULT 0,
            details TEXT NULL,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_integ_audit_user (user_id),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """
    ]

    async with engine.begin() as conn:
        for stmt in statements:
            try:
                await conn.execute(text(stmt))
            except Exception as e:
                logger.warning("Phase 11 Migration warning: %s", e)

    logger.info("Phase 11 DDL migrations applied successfully.")
