import bovine
from bovine.activitystreams import Actor

from bovine_store.types import ObjectType
from bovine_store.store.store import store_remote_object
from bovine_store.store.retrieve_object import retrieve_remote_object


class BovineApplicationActor(bovine.BovineActor):
    """Actor that represents the bovine application"""

    def __init__(self, config):
        config["public_key_url"] = config["account_url"] + "#main-key"
        super().__init__(config)

        self.actor_object = Actor(
            id=config["account_url"],
            preferred_username="bovine",
            public_key=config["public_key"],
            public_key_name="main-key",
            type="Application",
        ).build()

    async def store_remote_actor(self, item):
        return await store_remote_object(
            item.get("id", "NO_OWNER"),
            item,
            as_public=True,
            visible_to=[self.actor_object["id"]],
            object_type=ObjectType.REMOTE,
        )

    async def retrieve(self, key_url):
        return await retrieve_remote_object(self.actor_object["id"], key_url)
