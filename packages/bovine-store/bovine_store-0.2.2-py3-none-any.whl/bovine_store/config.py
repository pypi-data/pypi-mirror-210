import aiohttp
from quart import Quart

from bovine.crypto import build_validate_http_signature

from . import BovineStore
from .fedi.retrieve_public_key import retrieve_public_key


async def configure_bovine_store(app: Quart):
    """configures the quart app with a bovine_store"""
    if "session" not in app.config:
        app.config["session"] = aiohttp.ClientSession()

    app.config["bovine_store"] = BovineStore(
        session=app.config["session"],
    )

    app.config["validate_http_signature"] = build_validate_http_signature(
        retrieve_public_key
    )
