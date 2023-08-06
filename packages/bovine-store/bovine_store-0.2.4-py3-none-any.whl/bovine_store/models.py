from tortoise import fields
from tortoise.models import Model

from .types import VisibilityTypes, ObjectType, EndpointType


class StoredJsonObject(Model):
    """Stores an object"""

    id = fields.CharField(max_length=255, pk=True)
    owner = fields.CharField(max_length=255)

    content = fields.JSONField()
    created = fields.DatetimeField(auto_now_add=True)
    updated = fields.DatetimeField(auto_now=True)

    visibility = fields.CharEnumField(
        VisibilityTypes, default=VisibilityTypes.RESTRICTED
    )
    object_type = fields.CharEnumField(ObjectType, default=ObjectType.LOCAL)


class VisibleTo(Model):
    id = fields.IntField(pk=True)
    main_object = fields.ForeignKeyField(
        "models.StoredJsonObject", related_name="visible_to"
    )
    object_id = fields.CharField(max_length=255)


class CollectionItem(Model):
    id = fields.IntField(pk=True)
    part_of = fields.CharField(max_length=255)
    object_id = fields.CharField(
        max_length=255,
    )

    created = fields.DatetimeField(auto_now_add=True)
    updated = fields.DatetimeField(auto_now=True)


class BovineActor(Model):
    id = fields.IntField(pk=True)
    bovine_name = fields.CharField(max_length=255, unique=True)
    handle_name = fields.CharField(max_length=255)

    properties = fields.JSONField()

    created = fields.DatetimeField(auto_now_add=True)
    last_sign_in = fields.DatetimeField(auto_now=True)


class BovineActorEndpoint(Model):
    id = fields.IntField(pk=True)

    bovine_actor = fields.ForeignKeyField(
        "models.BovineActor", related_name="endpoints"
    )

    endpoint_type = fields.CharEnumField(enum_type=EndpointType)
    stream_name = fields.CharField(max_length=255)
    name = fields.CharField(max_length=255)


class BovineActorKeyPair(Model):
    id = fields.IntField(pk=True)

    bovine_actor = fields.ForeignKeyField("models.BovineActor", related_name="keypairs")

    name = fields.CharField(max_length=255)

    private_key = fields.TextField(null=True)  # FIXME Rename to secret
    public_key = fields.TextField()  # FIXME Rename to identity, Make unique

    # FIXME: Do we need a type, an order, a should display? Think about these things
    #
    # https://socialhub.activitypub.rocks/t/alsoknownas-and-acct/3132?u=helge
