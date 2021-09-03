import pytest
import asyncio
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine

# This needs to go above the create_app import
load_dotenv(".quartenv")

from application import create_app

# We need our own module-level event_loop
# since pytest's is a function-level fixture
@pytest.fixture(scope="session")
def event_loop(request):
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.mark.asyncio
@pytest.fixture
async def create_db():
    print("Creating db")
    db_name = os.environ["DATABASE_NAME"]
    db_host = os.environ["DB_HOST"]
    db_username = os.environ["DB_USERNAME"]
    db_password = os.environ["DB_PASSWORD"]

    db_uri = "postgresql://%s:%s@%s:5432/" % (
        db_username,
        db_password,
        db_host,
    )

    engine = create_engine(db_uri + db_name)
    conn = engine.connect()

    db_test_name = os.environ["DATABASE_NAME"] + "_test"
    conn.execute("commit")
    conn.execute("CREATE DATABASE " + db_test_name)
    conn.close()

    # TESTING flag disables error catching during request handling,
    # so that you get better error reports when performing test requests
    # against the application.
    yield {
        "DB_USERNAME": db_username,
        "DB_PASSWORD": db_password,
        "DB_HOST": db_host,
        "DATABASE_NAME": db_test_name,
        "DB_URI": db_uri + db_test_name,
        "TESTING": True,
    }

    print("Destroying db")
    engine = create_engine(db_uri + db_name)
    conn = engine.connect()

    # diconnect all users to test db
    # https://stackoverflow.com/a/63493002
    cmd = f"""
    SELECT pg_terminate_backend(pg_stat_activity.pid)
    FROM pg_stat_activity
    WHERE pg_stat_activity.datname = '{db_test_name}'
    AND pid <> pg_backend_pid();
    """
    conn.execute(cmd)
    conn.execute("COMMIT")
    conn.execute("DROP DATABASE " + db_test_name)
    conn.close()


@pytest.fixture
async def create_test_app(create_db):
    app = create_app(**create_db)
    await app.startup()
    yield app
    await app.shutdown()


@pytest.fixture
def create_test_client(create_test_app):
    print("Creating test client")
    return create_test_app.test_client()
