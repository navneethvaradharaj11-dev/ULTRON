import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Server
    PORT: int = 8000
    HOST: str = "127.0.0.1"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"

    # MySQL Database Settings (Pure MySQL as primary database)
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = "root"
    MYSQL_DATABASE: str = "ultron_db"

    # Security
    JWT_SECRET: str = "ultron_super_secret_jwt_key_change_in_production_32bytes"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # AI Provider ('gemini', 'openai', 'anthropic', or 'mock')
    AI_PROVIDER: str = "mock"
    AI_MODEL_NAME: str = "gemini-2.5-flash"
    AI_API_KEY: str = "mock_key"

    # Voice Engine
    VOICE_ENGINE: str = "mock"
    STT_PROVIDER: str = "mock"
    TTS_PROVIDER: str = "mock"

    # System Safety & Execution Limits
    MAX_AGENT_STEPS: int = 10
    MAX_TOOL_CALLS: int = 5
    MAX_CONTEXT_MESSAGES: int = 20
    TOOL_TIMEOUT: float = 10.0
    MODEL_TIMEOUT: float = 30.0

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(__file__), "../../.env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def database_url_async(self) -> str:
        """Async SQLAlchemy Database URL for aiomysql."""
        return f"mysql+aiomysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"

    @property
    def database_url_sync(self) -> str:
        """Sync SQLAlchemy Database URL for pymysql (schema migrations / admin)."""
        return f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"


settings = Settings()
