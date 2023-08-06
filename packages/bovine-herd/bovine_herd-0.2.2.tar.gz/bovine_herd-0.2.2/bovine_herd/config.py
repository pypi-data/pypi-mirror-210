import os

import aiohttp

db_url = os.environ.get("BOVINE_DB_URL", "sqlite://bovine.sqlite3")

TORTOISE_ORM = {
    "connections": {"default": db_url},
    "apps": {
        "models": {
            "models": [
                "bovine_store.models",
            ],
            "default_connection": "default",
        },
    },
}


async def configure_bovine_herd(app):
    if "session" not in app.config:
        session = aiohttp.ClientSession()
        app.config["session"] = session
