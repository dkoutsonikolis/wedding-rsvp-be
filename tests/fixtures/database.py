import os
from urllib.parse import urlparse, urlunparse

import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from config import settings

TEST_DATABASE_NAME = "app_db_test"


def _adjust_hostname(database_url: str) -> str:
    """
    Adjust database URL hostname for local vs Docker execution.

    When running tests locally from the host machine, the DATABASE_URL might use 'db' as
    the hostname (Docker service name), but we need 'localhost' to connect from the host.
    When running tests inside a Docker container, we should use 'db' as-is since it resolves
    correctly within the Docker network.
    """
    parsed = urlparse(database_url)

    # Only replace 'db' with 'localhost' if we're running from the host machine
    # Check if we're inside Docker by looking for /.dockerenv file
    is_inside_docker = os.path.exists("/.dockerenv")

    # Replace 'db' hostname with 'localhost' only when running from host machine
    if parsed.hostname == "db" and not is_inside_docker:
        # Reconstruct netloc with localhost
        # netloc format: username:password@hostname:port
        if parsed.username and parsed.password:
            # Has authentication
            auth = f"{parsed.username}:{parsed.password}@"
        elif parsed.username:
            # Username only
            auth = f"{parsed.username}@"
        else:
            # No authentication
            auth = ""

        # Reconstruct netloc with localhost
        port_part = f":{parsed.port}" if parsed.port else ""
        new_netloc = f"{auth}localhost{port_part}"

        # Reconstruct URL with localhost
        new_parsed = parsed._replace(netloc=new_netloc)
        database_url = urlunparse(new_parsed)

    return database_url


def get_admin_database_url() -> str:
    """
    Get the admin database URL (connects to 'postgres' database for creating/dropping databases).

    This is used to connect to the default 'postgres' database to create or drop the test database.
    """
    database_url = os.getenv("DATABASE_URL", settings.DATABASE_URL)
    parsed = urlparse(database_url)

    # Replace the database name with 'postgres' (default admin database)
    new_path = "/postgres"
    new_parsed = parsed._replace(path=new_path)
    admin_url = urlunparse(new_parsed)

    return _adjust_hostname(admin_url)


def get_test_database_url() -> str:
    """
    Get the test database URL pointing to the isolated test database.

    This URL points to a database separate from the development database.
    """
    database_url = os.getenv("DATABASE_URL", settings.DATABASE_URL)
    parsed = urlparse(database_url)

    # Replace the database name with the test database name
    new_path = f"/{TEST_DATABASE_NAME}"
    new_parsed = parsed._replace(path=new_path)
    test_url = urlunparse(new_parsed)

    return _adjust_hostname(test_url)


@pytest_asyncio.fixture(scope="session")
async def test_database():
    """
    Create the test database before tests run and drop it after all tests complete.

    This fixture is session-scoped, so it runs once per test session.
    """
    admin_url = get_admin_database_url()
    admin_engine = create_async_engine(admin_url, echo=False, pool_pre_ping=True)

    # Create the test database
    # DROP/CREATE DATABASE must run outside a transaction (autocommit mode)
    async with admin_engine.connect() as conn:
        # Get the underlying asyncpg connection
        raw_conn = await conn.get_raw_connection()
        asyncpg_conn = raw_conn.driver_connection

        # Terminate any existing connections to the test database
        try:
            await asyncpg_conn.execute(
                f"""
                SELECT pg_terminate_backend(pg_stat_activity.pid)
                FROM pg_stat_activity
                WHERE pg_stat_activity.datname = '{TEST_DATABASE_NAME}'
                AND pid <> pg_backend_pid();
                """
            )
        except Exception:
            # Ignore errors if there are no connections to terminate
            pass

        # Drop the database if it exists (autocommit by default for asyncpg)
        await asyncpg_conn.execute(f"DROP DATABASE IF EXISTS {TEST_DATABASE_NAME};")
        # Create the test database
        await asyncpg_conn.execute(f"CREATE DATABASE {TEST_DATABASE_NAME};")

    await admin_engine.dispose()

    yield

    # Cleanup: drop the test database after all tests complete
    admin_engine = create_async_engine(admin_url, echo=False, pool_pre_ping=True)
    async with admin_engine.connect() as conn:
        # Get the underlying asyncpg connection
        raw_conn = await conn.get_raw_connection()
        asyncpg_conn = raw_conn.driver_connection

        # Terminate any existing connections to the test database
        try:
            await asyncpg_conn.execute(
                f"""
                SELECT pg_terminate_backend(pg_stat_activity.pid)
                FROM pg_stat_activity
                WHERE pg_stat_activity.datname = '{TEST_DATABASE_NAME}'
                AND pid <> pg_backend_pid();
                """
            )
        except Exception:
            # Ignore errors if there are no connections to terminate
            pass

        # Drop the test database (autocommit by default for asyncpg)
        await asyncpg_conn.execute(f"DROP DATABASE IF EXISTS {TEST_DATABASE_NAME};")
    await admin_engine.dispose()


@pytest_asyncio.fixture
async def test_engine(test_database):
    """
    Create a test database engine connected to the test database.

    This fixture depends on test_database to ensure the test database exists.
    """
    test_url = get_test_database_url()
    engine = create_async_engine(
        test_url,
        echo=False,
        pool_pre_ping=True,
    )

    # Register all SQLModel table classes before create_all
    import domains.anonymous_agent_sessions.models  # noqa: F401
    import domains.contact.models  # noqa: F401
    import domains.users.models  # noqa: F401
    import domains.wedding_sites.models  # noqa: F401

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    yield engine

    # Cleanup: drop all tables after tests
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def test_session(test_engine):
    """Create a test database session."""
    async_session = sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        yield session
