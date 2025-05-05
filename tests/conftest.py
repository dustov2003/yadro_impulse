from asyncio import get_event_loop_policy
from os import environ
from types import SimpleNamespace
from typing import Any, AsyncGenerator, Generator
from uuid import uuid4

import pytest
from alembic.command import upgrade
from alembic.config import Config
import unittest.mock as mock
from mock import AsyncMock
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import create_database, database_exists, drop_database
from fastapi.testclient import TestClient

from tests.utils import make_alembic_config

import dag_service.utils as utils_module
from dag_service.__main__ import get_app
from dag_service.config.utils import get_settings
from dag_service.db.connection import SessionManager
from dag_service.db.models import *



@pytest.fixture(scope="session")
def event_loop():
    policy = get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture()
def postgres() -> Generator[str, Any, None]:
    settings = get_settings()

    tmp_name = ".".join([uuid4().hex, "pytest"])
    settings.POSTGRES_DB = tmp_name
    environ["POSTGRES_DB"] = tmp_name

    tmp_url = settings.database_uri_sync
    if not database_exists(tmp_url):
        create_database(tmp_url)

    try:
        yield settings.database_uri
    finally:
        drop_database(tmp_url)


def run_upgrade(connection, cfg):
    cfg.attributes["connection"] = connection
    upgrade(cfg, "head")


async def run_async_upgrade(config: Config, database_uri: str):
    async_engine = create_async_engine(database_uri, echo=True)
    async with async_engine.begin() as conn:
        await conn.run_sync(run_upgrade, config)


@pytest.fixture
def alembic_config(postgres) -> Config:
    cmd_options = SimpleNamespace(config="dag_service/db/", name="alembic", pg_url=postgres, raiseerr=False, x=None)
    return make_alembic_config(cmd_options)


@pytest.fixture
def alembic_engine():
    settings = get_settings()
    return create_async_engine(settings.database_uri_sync, echo=True)


@pytest.fixture
async def migrated_postgres(postgres, alembic_config: Config):
    await run_async_upgrade(alembic_config, postgres)


@pytest.fixture
def client(migrated_postgres, manager: SessionManager = SessionManager()) -> TestClient:
    app = get_app()
    manager.refresh()
    utils_module.check_website_exist = mock.AsyncMock(return_value=(True, "Status code < 400"))
    return TestClient(app=app, base_url="http://test")


@pytest.fixture
async def engine_async(postgres) -> AsyncGenerator[AsyncEngine, Any]:
    engine = create_async_engine(postgres, future=True)
    yield engine
    await engine.dispose()


@pytest.fixture
def session_factory_async(engine_async) -> sessionmaker:
    return sessionmaker(engine_async, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture
async def session(session_factory_async):
    async with session_factory_async() as session:
        yield session


@pytest.fixture
async def dag_sample(migrated_postgres, session: AsyncSession):
    dag = DAG()
    session.add(dag)
    await session.flush()
    dag_id = dag.dag_id

    node_a = Node(dag_id=dag_id, name="A")
    node_b = Node(dag_id=dag_id, name="B")
    node_c = Node(dag_id=dag_id, name="C")
    node_d = Node(dag_id=dag_id, name="D")
    node_e = Node(dag_id=dag_id, name="E")
    session.add_all([node_a, node_b, node_c, node_d, node_e])
    await session.flush()

    edge_ab = Edge(dag_id=dag_id, source="A", target="B")
    edge_bc = Edge(dag_id=dag_id, source="B", target="C")
    edge_cd = Edge(dag_id=dag_id, source="C", target="D")
    edge_de = Edge(dag_id=dag_id, source="D", target="E")
    edge_ac = Edge(dag_id=dag_id, source="A", target="C")
    session.add_all([edge_ab, edge_bc, edge_cd, edge_de, edge_ac])
    await session.flush()

    await session.commit()
    return dag_id