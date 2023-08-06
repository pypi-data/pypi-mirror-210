import logging

from urllib.parse import urlparse
from quart import g, current_app, request

from bovine.crypto import validate_moo_auth_signature

logger = logging.getLogger(__name__)


async def compute_moo_auth_result():
    # FIXME: Should use a cache and allow for remote lookup

    domain = urlparse(request.url).netloc
    didkey, remote_domain = await validate_moo_auth_signature(request, domain)

    if remote_domain:
        logger.warning(
            "Lookup with did:key %s from remote domain %s", didkey, remote_domain
        )

    _, actor_id = await current_app.config["bovine_store"].get_name_url_for_did(didkey)

    return actor_id


async def add_authorization():
    if g.get("retriever"):
        return

    if "authorization" in request.headers and request.headers[
        "authorization"
    ].startswith("Moo-Auth-1"):
        g.retriever = await compute_moo_auth_result()
        return

    g.retriever = await current_app.config["validate_http_signature"](request)
