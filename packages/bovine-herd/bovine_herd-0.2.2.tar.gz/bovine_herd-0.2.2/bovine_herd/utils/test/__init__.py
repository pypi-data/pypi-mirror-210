# import os

import pytest
from bovine_store.utils.test import store, test_app  # noqa F401
from tortoise import Tortoise, connections

from bovine_herd.server import default_configuration
from bovine_herd.utils import init


@pytest.fixture
async def fedi_test_app(test_app):  # noqa F801
    test_app.register_blueprint(default_configuration)
    yield test_app


def remove_domain_from_url(url):
    assert url.startswith("https://my_domain")

    return url[17:]


@pytest.fixture
async def db_url() -> str:
    # db_file = "test_db.sqlite3"
    # db_url = f"sqlite://{db_file}"
    db_url = "postgres://postgres:secret@localhost:5432/postgres"

    await init(db_url)

    yield db_url

    await Tortoise.close_connections()
    connection = connections.get("default")
    for table in [
        "visibleto",
        "bovineuserendpoint",
        "bovineuserkeypair",
        "bovineuserproperty",
        "collectionitem",
        "storedjsonobject",
        "bovineuser",
    ]:
        await connection.execute_query(f"DROP TABLE IF EXISTS {table}")
    # os.unlink(db_file)
