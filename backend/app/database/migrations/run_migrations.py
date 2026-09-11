import os
import pymysql
import logging
from app.config.settings import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ULTRON.Migrations")


def run_migrations(version: str = "v11.0.0"):
    """Execute raw SQL migrations from schema.sql against MySQL instance with version tracking."""
    logger.info("Checking database migrations on MySQL server (%s:%s)...", settings.MYSQL_HOST, settings.MYSQL_PORT)
    
    try:
        conn = pymysql.connect(
            host=settings.MYSQL_HOST,
            port=settings.MYSQL_PORT,
            user=settings.MYSQL_USER,
            password=settings.MYSQL_PASSWORD,
            autocommit=True
        )
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {settings.MYSQL_DATABASE} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
        cursor.execute(f"USE {settings.MYSQL_DATABASE};")

        # Version tracking table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version VARCHAR(64) PRIMARY KEY,
                applied_at DATETIME NOT NULL
            );
        """)
        cursor.execute("SELECT version FROM schema_migrations WHERE version = %s;", (version,))
        if cursor.fetchone():
            logger.info("Database schema version '%s' is already applied. Skipping DDL execution.", version)
            cursor.close()
            conn.close()
            return

        schema_path = os.path.join(os.path.dirname(__file__), "../../../database/schema.sql")
        with open(schema_path, "r", encoding="utf-8") as f:
            schema_sql = f.read()

        statements = [stmt.strip() for stmt in schema_sql.split(";") if stmt.strip()]
        for statement in statements:
            if statement.upper().startswith("USE "):
                continue
            cursor.execute(statement)

        cursor.execute("INSERT INTO schema_migrations (version, applied_at) VALUES (%s, NOW());", (version,))
        logger.info("Database migration '%s' completed successfully.", version)
        cursor.close()
        conn.close()
    except Exception as e:
        logger.warning("Database migration skipped (MySQL server offline or credentials pending): %s", e)


if __name__ == "__main__":
    run_migrations()

