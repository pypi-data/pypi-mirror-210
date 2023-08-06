import asyncio

from bovine.jsonld import split_into_objects
from bovine_store.types import ObjectType
from bovine_store.models import StoredJsonObject, VisibleTo


async def update_remote_object(
    owner, item, visible_to=[], object_type=ObjectType.LOCAL
):
    # FIXME Currently update does not handle visibility changes

    to_store = await split_into_objects(item)

    tasks = [
        StoredJsonObject.update_or_create(
            id=obj["id"],
            defaults={"owner": owner, "content": obj, "object_type": object_type},
        )
        for obj in to_store
    ]

    items = await asyncio.gather(*tasks)

    for item, created in items:
        visible_tasks = [
            VisibleTo.get_or_create(
                main_object=item,
                object_id=actor,
            )
            for actor in visible_to
        ]
        await asyncio.gather(*visible_tasks)

    return items


async def remove_remote_object(remover, object_id):
    result = await StoredJsonObject.get_or_none(id=object_id)

    if result and result.owner == remover:
        await result.delete()
