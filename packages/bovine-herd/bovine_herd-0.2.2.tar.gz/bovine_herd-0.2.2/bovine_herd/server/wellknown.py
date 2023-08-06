import logging
from urllib.parse import urljoin

from bovine.utils import webfinger_response_json
from bovine_store.utils import path_from_request
from quart import Blueprint, current_app, request

wellknown = Blueprint("wellknown", __name__, url_prefix="/.well-known")

logger = logging.getLogger(__name__)


@wellknown.get("/nodeinfo")
async def nodeinfo() -> tuple[dict, int]:
    domain = request.host

    return {
        "links": [
            {
                "rel": "http://nodeinfo.diaspora.software/ns/schema/2.0",
                "href": f"https://{domain}/info/nodeinfo2_0",
            }
        ]
    }, 200


@wellknown.get("/webfinger")
async def webfinger() -> tuple[dict, int]:
    resource = request.args.get("resource")

    if not resource:
        return {"error": "invalid request"}, 400

    if not resource.startswith("did:") and not resource.startswith("acct:"):
        return {"error": "invalid request"}, 400

    return await webfinger_response(resource)


async def webfinger_response(resource):
    domain = request.host
    name = None

    if resource == f"acct:bovine@{domain}":
        name = "bovine"
        url = f"https://{domain}/activitypub/bovine"
    else:
        logger.debug("Got resource %s", resource)
        bovine_store = current_app.config["bovine_store"]
        name, url = await bovine_store.get_name_url_for_did(resource)

        if not name:
            return {"status": "not found"}, 404

    return (
        webfinger_response_json(name, url, domain),
        200,
        {"content-type": "application/jrd+json"},
    )


@wellknown.get("/host-meta")
async def wellknown_host_meta():
    path = path_from_request(request)

    webfinger = urljoin(path, "webfinger")

    return (
        f"""<?xml version="1.0" encoding="UTF-8"?>
<XRD xmlns="http://docs.oasis-open.org/ns/xri/xrd-1.0">
  <Link rel="lrdd" template="{webfinger}?resource={{uri}}"/>
</XRD>""",
        200,
        {"content-type": "application/xrd+xml"},
    )
