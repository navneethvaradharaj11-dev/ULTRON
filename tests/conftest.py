import json
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.database.connection import Base, get_db
from app.database.models import AgentModel, User
from app.database.seeds.initial_seeds import INITIAL_AGENTS
from app.security.authentication import get_password_hash
from app.main import app

# Shared In-Memory SQLite Engine for Pytest Multi-Threaded WebSocket Testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///file:testdb?mode=memory&cache=shared&uri=true"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)


@pytest_asyncio.fixture(autouse=True, scope="function")
async def setup_test_database():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Seed agents & test user into test database
    async with TestingSessionLocal() as session:
        test_user = User(
            id="test_user_id",
            username="testuser",
            email="testuser@ultron.ai",
            password_hash=get_password_hash("SecretPassword123")
        )
        session.add(test_user)

        for agent in INITIAL_AGENTS:
            agent_model = AgentModel(
                id=agent["id"],
                name=agent["name"],
                code_name=agent["code_name"],
                description=agent["description"],
                capabilities_json=agent["capabilities_json"],
                status=agent["status"]
            )
            session.add(agent_model)
        await session.commit()

    yield

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await test_engine.dispose()


@pytest_asyncio.fixture
async def db_session():
    async with TestingSessionLocal() as session:
        yield session


async def override_get_db():
    async with TestingSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


app.dependency_overrides[get_db] = override_get_db
