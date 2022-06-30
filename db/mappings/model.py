import enum

from peewee import TextField

from db.mappings.base import BaseMapping


class Type(enum.Enum):
    ARTICLE = "article"
    USER = "user"
    POPULARITY = "popularity"


class Status(enum.Enum):
    PENDING = "pending"
    CURRENT = "current"
    STALE = "stale"
    FAILED = "failed"


class Site(enum.Enum):
    WCP = "washington-city-paper"
    PHILLY_INQUIRER = "philadelphia-inquirer"
    TEXAS_TRIBUNE = "texas-tribune"


class Model(BaseMapping):
    class Meta:
        table_name = "model"

    type = TextField(null=False)
    status = TextField(null=False, default=Status.PENDING.value)
    site = TextField(null=False, default="")
