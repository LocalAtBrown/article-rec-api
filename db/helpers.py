import psycopg2.errors
import logging

from peewee import Expression

from db.mappings.base import BaseMapping, tzaware_now
from lib.db import db


def create_resource(mapping_class: BaseMapping, **params: dict) -> int:
    resource = mapping_class(**params)
    resource.save()
    return resource.id


def get_resource(mapping_class: BaseMapping, _id: int) -> dict:
    instance = mapping_class.get(mapping_class.id == _id)
    return instance.to_dict()


def update_resources(
    mapping_class: BaseMapping, conditions: Expression, **params: dict
) -> None:
    params["updated_at"] = tzaware_now()
    q = mapping_class.update(**params).where(conditions)
    q.execute()


def retry_rollback(f):
    def decorated(self, *args, **kwargs):
        with db.transaction() as txn:
            try:
                result = f(self, *args, **kwargs)
            except psycopg2.errors.InFailedSqlTransaction:
                txn.rollback()
                logging.info("Rolling back failed transaction.")
                result = f(self, *args, **kwargs)
        return result
    return decorated
