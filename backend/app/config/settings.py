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

    # AI Provider ('gemini', 'openai', 'anthropic', 'ollama', or 'mock')
    AI_PROVIDER: str = "gemini"
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

    # Phase 3: Browser Limits & Policy Settings
    BROWSER_ALLOWED_DOMAINS: str = "*"
    MAX_BROWSER_STEPS: int = 15
    MAX_NAVIGATIONS: int = 5
    MAX_CLICKS: int = 10
    MAX_PAGE_READS: int = 10
    BROWSER_ACTION_TIMEOUT: float = 15.0

    # Phase 4: Code Execution & Sandbox Limits
    CODE_EXECUTION_TIMEOUT: float = 10.0
    CODE_MAX_CPU_SECONDS: int = 10
    CODE_MAX_MEMORY_MB: int = 512
    CODE_MAX_OUTPUT_BYTES: int = 1048576
    CODE_MAX_FILE_SIZE_MB: int = 10
    CODE_MAX_FILES: int = 100
    CODE_MAX_PROCESSES: int = 10
    CODE_MAX_RETRIES: int = 3
    CODE_MAX_EXECUTIONS_PER_TASK: int = 5
    CODE_MAX_WORKSPACE_SIZE_MB: int = 100
    SANDBOX_PREFER_DOCKER: bool = True

    # Phase 5: Perception Engine & Computer Interaction Settings
    VISION_PROVIDER: str = "mock"
    VISION_MODEL: str = "gemini-2.5-flash"
    VISION_TIMEOUT: float = 15.0
    VISION_CONFIDENCE_THRESHOLD: float = 0.85
    VISION_LOW_CONFIDENCE_THRESHOLD: float = 0.60
    MAX_COMPUTER_ACTIONS: int = 20
    MAX_MOUSE_ACTIONS: int = 15
    MAX_KEYBOARD_ACTIONS: int = 15
    MAX_SCREENSHOTS: int = 20
    MAX_PERCEPTION_CALLS: int = 20
    COMPUTER_ACTION_TIMEOUT: float = 10.0
    SCREENSHOT_RETENTION_SECONDS: int = 3600
    COMPUTER_APPROVAL_REQUIRED: bool = True




    # Phase 12.8 Version & Control Identity
    VERSION: str = "12.8.0"
    EMERGENCY_SHUTDOWN_ACTIVE: bool = False

    # Phase 12: Production Infrastructure & Operations
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = ""
    REDIS_DB: int = 0
    CORS_ALLOWED_ORIGINS: str = "http://100.69.161.16:8000"
    RATE_LIMIT_PER_MINUTE: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(__file__), "../../../.env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    def validate_production_secrets(self) -> None:
        """Startup check: Fail closed if running in production with default secrets."""
        if self.ENVIRONMENT.lower() == "production":
            if "change_in_production" in self.JWT_SECRET or len(self.JWT_SECRET) < 32:
                raise ValueError("SECURITY RISK: Default or weak JWT_SECRET cannot be used in production environment.")
            if self.MYSQL_PASSWORD == "root":
                raise ValueError("SECURITY RISK: Default MYSQL_PASSWORD 'root' cannot be used in production environment.")
            if self.DEBUG:
                raise ValueError("SECURITY RISK: DEBUG mode must be False in production environment.")
            if self.CORS_ALLOWED_ORIGINS == "*":
                raise ValueError("SECURITY RISK: Wildcard CORS_ALLOWED_ORIGINS '*' is prohibited in production environment.")

    @property
    def database_url_async(self) -> str:
        """Async SQLAlchemy Database URL for aiomysql."""
        return f"mysql+aiomysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"

    @property
    def database_url_sync(self) -> str:
        """Sync SQLAlchemy Database URL for pymysql (schema migrations / admin)."""
        return f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"


settings = Settings()

