import enum

from peewee import TextField

from db.mappings.base import BaseMapping


class Type(enum.Enum):
    ARTICLE = "article"
    USER = "user"


class Status(enum.Enum):
    PENDING = "pending"
    CURRENT = "current"
    STALE = "stale"
    FAILED = "failed"


class Model(BaseMapping):
    class Meta:
        table_name = "model"

    type = TextField(null=False)
    status = TextField(null=False, default=Status.PENDING.value)
