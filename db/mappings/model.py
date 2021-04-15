import enum
import logging

from peewee import TextField

from db.mappings.base import BaseMapping
from db.helpers import update_resources
from lib.db import db


class Type(enum.Enum):
    ARTICLE = "article"
    USER = "user"
    POPULARITY = "popularity"


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

    # If an exception occurs, the current transaction/savepoint will be rolled back.
    # Otherwise the statements will be committed at the end.
    @db.atomic()
    def set_current(model_id: int, model_type: Type) -> None:
        current_model_query = (Model.type == model_type) & (
            Model.status == Status.CURRENT.value
        )
        update_resources(Model, current_model_query, status=Status.STALE.value)
        update_resources(Model, Model.id == model_id, status=Status.CURRENT.value)
        logging.info(
            f"Successfully updated model id {model_id} as current '{model_type}' model"
        )
