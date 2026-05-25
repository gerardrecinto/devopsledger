import asyncio
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.db import get_db
from app.main import app
from app.models.base import Base

_DB_PATH = Path("/tmp/devopsledger_test.db")
_DB_URL = f"sqlite+aiosqlite:///{_DB_PATH}"


@pytest.fixture()
def client():
    """Test client with isolated file-based SQLite DB, reset each test."""
    _DB_PATH.unlink(missing_ok=True)

    engine = create_async_engine(_DB_URL, poolclass=NullPool)

    async def _setup():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    asyncio.run(_setup())

    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async def _override_db():
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = _override_db

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()

    async def _teardown():
        await engine.dispose()

    asyncio.run(_teardown())
    _DB_PATH.unlink(missing_ok=True)
