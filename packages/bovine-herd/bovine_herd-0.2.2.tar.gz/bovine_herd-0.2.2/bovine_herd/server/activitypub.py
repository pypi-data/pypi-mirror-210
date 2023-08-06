import logging

import werkzeug
from bovine_store.utils import path_from_request
from quart import Blueprint, current_app, request

activitypub = Blueprint("activitypub", __name__, url_prefix="/activitypub")

logger = logging.getLogger(__name__)


@activitypub.get("/<account_name>")
async def userinfo(account_name: str) -> tuple[dict, int] | werkzeug.Response:
    if account_name != "bovine":
        return {"status": "not found"}, 404

    store = current_app.config["bovine_store"]
    path = path_from_request(request)
    actor = await store.application_actor_for_url(path)

    return (
        actor.actor_object,
        200,
        {"content-type": "application/activity+json"},
    )
