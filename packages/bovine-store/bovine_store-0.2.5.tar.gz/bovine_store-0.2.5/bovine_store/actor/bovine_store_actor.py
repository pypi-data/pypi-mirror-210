import asyncio
from datetime import datetime, timedelta, timezone
import logging
import traceback
import uuid
from urllib.parse import urljoin

from typing import Optional, List

from bovine import BovineActor
from bovine.activitystreams import Actor
from bovine.jsonld import combine_items

from bovine_store.store.store import store_remote_object
from bovine_store.store.remote import update_remote_object
from bovine_store.store.retrieve_object import retrieve_remote_object
from bovine_store.models import StoredJsonObject, CollectionItem
from bovine_store.types import EndpointType, ObjectType
from bovine_store.store.utils import domain_from_host
from bovine_store.store.collection import collection_all

logger = logging.getLogger(__name__)


class BovineStoreActor(BovineActor):
    def __init__(self, config: dict, actor_object: Actor, endpoints: List[str] = []):
        self.actor_object: Actor = actor_object

        self.domain = domain_from_host(actor_object.id)
        self.endpoints = endpoints

        super().__init__(config)

    async def retrieve(self, object_id: str, include=[], skip_fetch: bool = False):
        data = await self._retrieve_object_from_database(
            object_id, skip_fetch=skip_fetch
        )

        if data is None:
            return data

        if len(include) == 0:
            return data

        items = await asyncio.gather(
            *[
                self._retrieve_object_from_database(data[key])
                for key in include
                if key in data
            ]
        )

        return combine_items(data, items)

    async def _retrieve_object_from_database(
        self, object_id, skip_fetch: bool = False
    ) -> Optional[dict]:
        try:
            result = await StoredJsonObject.get_or_none(id=object_id)

            if skip_fetch:
                if result:
                    return result.content
                return None

            if not BovineStoreActor._is_stale(result):
                return result.content

            obj = await self.get(object_id)
            if "attributedTo" in obj:
                owner = obj["attributedTo"]
            elif "actor" in obj:
                owner = obj["actor"]
            else:
                owner = object_id

            logger.info("Storing %s", obj["id"])

            await update_remote_object(
                owner,
                obj,
                visible_to=[self.actor_object.id],
                object_type=ObjectType.REMOTE,
            )

            return obj
        except Exception as ex:
            logger.info("Failed to retrieve %s with %s", object_id, ex)
            for log_line in traceback.format_exc().splitlines():
                logger.info(log_line)

            return None

    async def store(self, item, as_public: bool = False, visible_to=[]):
        return await store_remote_object(
            self.actor_id,
            item,
            as_public=as_public,
            visible_to=visible_to,
            object_type=ObjectType.LOCAL,
        )

    async def update(self, item):
        await update_remote_object(self.actor_object.id, item)

    async def retrieve_for(self, retriever, object_id, include=[]):
        return await retrieve_remote_object(retriever, object_id, include=include)

    async def store_for(self, owner, item, as_public=False, visible_to=[]):
        return await store_remote_object(
            owner, item, as_public=as_public, visible_to=visible_to, domain=self.domain
        )

    async def update_for(self, owner, item):
        return await update_remote_object(owner, item)

    async def add_to_outbox(self, object_id):
        return await CollectionItem.create(
            part_of=self.actor_object.outbox, object_id=object_id
        )

    async def add_to_inbox(self, object_id):
        return await CollectionItem.create(
            part_of=self.actor_object.inbox, object_id=object_id
        )

    async def add_to_followers(self, object_id):
        return await CollectionItem.create(
            part_of=self.actor_object.followers, object_id=object_id
        )

    async def add_to_following(self, object_id):
        return await CollectionItem.create(
            part_of=self.actor_object.following, object_id=object_id
        )

    async def resolve_endpoints(self, endpoints):
        tasks = [collection_all(self.actor_id, endpoint) for endpoint in endpoints]
        result = await asyncio.gather(*tasks)
        result = set(sum(result, []))

        logger.info("Resolved %s to %s", ", ".join(endpoints), ", ".join(result))
        return result

    def generate_new_object_id(self) -> str:
        return urljoin(self.actor_object.id, "/objects/" + str(uuid.uuid4()))

    @staticmethod
    def _is_stale(result):
        if result is None:
            return True
        if result.object_type == ObjectType.LOCAL:
            return False

        updated = result.updated
        updated = updated.replace(tzinfo=timezone.utc)

        return updated < (datetime.now(tz=timezone.utc) - timedelta(days=1))

    @staticmethod
    async def from_database(user, session):
        mapped_endpoints = {x.endpoint_type: x for x in user.endpoints}
        account_url = mapped_endpoints[EndpointType.ACTOR].name

        def get_server_key(user):
            for iter_keypair in user.keypairs:
                if iter_keypair.name == "serverKey":
                    return iter_keypair
            return user.keypairs[0]

        keypair = get_server_key(user)
        public_key_url = f"{account_url}#{keypair.name}"

        config = {
            "account_url": account_url,
            "public_key_url": public_key_url,
            "private_key": keypair.private_key,
        }

        endpoints = [
            x.name
            for x in user.endpoints
            if x.endpoint_type in [EndpointType.FOLLOWERS, EndpointType.COLLECTION]
        ]

        actor_object = Actor(
            id=account_url,
            preferred_username=user.handle_name,
            inbox=mapped_endpoints[EndpointType.INBOX].name,
            outbox=mapped_endpoints[EndpointType.OUTBOX].name,
            event_source=mapped_endpoints[EndpointType.EVENT_SOURCE].name,
            followers=mapped_endpoints[EndpointType.FOLLOWERS].name,
            following=mapped_endpoints[EndpointType.FOLLOWING].name,
            proxy_url=mapped_endpoints[EndpointType.PROXY_URL].name,
            public_key=keypair.public_key,
            public_key_name=keypair.name,
        )

        if "type" in user.properties:
            actor_object.type = user.properties["type"]
        if "name" in user.properties:
            actor_object.name = user.properties["name"]
        if "summary" in user.properties:
            actor_object.summary = user.properties["summary"]
        if "icon" in user.properties:
            actor_object.icon = user.properties["icon"]

        actor = BovineStoreActor(config, actor_object, endpoints=endpoints)
        await actor.init(session=session)

        return actor
