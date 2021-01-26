import enum

from peewee import TextField

from db.mappings.base import BaseMapping


class Type(enum.Enum):
    # in the future, we imagine supporting 'user' and 'cluster' types
    ARTICLE = "article"


class Status(enum.Enum):
    PENDING = "pending"
    CURRENT = "current"
    STALE = "stale"
    FAILED = "failed"


class Model(BaseMapping):
    class Meta:
        db_table = "model"

    type = TextField(null=False)
    status = TextField(null=False, default=Status.PENDING.value)
