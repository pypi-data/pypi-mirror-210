import os

import aiohttp
from bovine_pubsub import configure_bovine_pub_sub
from bovine_store.blueprint import bovine_store_blueprint
from bovine_store.config import configure_bovine_store, tortoise_config
from quart import Quart
from quart_redis import RedisHandler
from tortoise.contrib.quart import register_tortoise

from .server import default_configuration
from .server.endpoints import endpoints


def bovine_herd(app: Quart) -> Quart:
    """Configures the quart app to use bovine herd"""
    redis_url = os.environ.get("BOVINE_REDIS")
    db_url = os.environ.get("BOVINE_DB_URL", "sqlite://bovine.sqlite3")

    if redis_url:
        app.config["REDIS_URI"] = redis_url
        RedisHandler(app)

    @app.before_serving
    async def startup():
        if "session" not in app.config:
            session = aiohttp.ClientSession()
            app.config["session"] = session
        await configure_bovine_store(app)
        await configure_bovine_pub_sub(app)

    @app.after_serving
    async def shutdown():
        await app.config["session"].close()

    app.register_blueprint(default_configuration)
    app.register_blueprint(endpoints, url_prefix="/endpoints")
    app.register_blueprint(bovine_store_blueprint, url_prefix="/objects")

    TORTOISE_ORM = tortoise_config(db_url)

    register_tortoise(
        app,
        db_url=TORTOISE_ORM["connections"]["default"],
        modules={"models": TORTOISE_ORM["apps"]["models"]["models"]},
        generate_schemas=True,
    )

    return app
