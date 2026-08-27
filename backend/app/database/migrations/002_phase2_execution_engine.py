import os
import pymysql
import logging
from app.config.settings import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ULTRON.Migrations.Phase2")


def run_phase2_migration():
    """Execute migration to ensure Phase 2 execution engine tables exist in MySQL."""
    logger.info("Running Phase 2 database migration on MySQL...")
    conn = pymysql.connect(
        host=settings.MYSQL_HOST,
        port=settings.MYSQL_PORT,
        user=settings.MYSQL_USER,
        password=settings.MYSQL_PASSWORD,
        database=settings.MYSQL_DATABASE,
        autocommit=True
    )
    cursor = conn.cursor()
    
    schema_path = os.path.join(os.path.dirname(__file__), "../../../database/schema.sql")
    with open(schema_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    statements = [stmt.strip() for stmt in schema_sql.split(";") if stmt.strip()]
    for statement in statements:
        if statement.upper().startswith("USE "):
            continue
        cursor.execute(statement)

    logger.info("Phase 2 database tables verified/created successfully.")
    cursor.close()
    conn.close()


if __name__ == "__main__":
    run_phase2_migration()
