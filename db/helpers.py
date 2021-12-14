import logging
from typing import List

import psycopg2.errors
from peewee import Expression, InterfaceError

from db.mappings.base import BaseMapping, tzaware_now
from db.mappings.article import Article
from lib.db import db
from lib.config import config


MAX_PAGE_SIZE = config.get("MAX_PAGE_SIZE")


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


def get_articles_by_external_ids(site: str, external_ids: List[str]) -> List[dict]:
    res = (
        Article.select()
        .where((Article.site == site))
        .where(Article.external_id.in_(list(external_ids)))
        .order_by(Article.published_at.desc())
        .limit(MAX_PAGE_SIZE)
    )
    if res:
        return [r.to_dict() for r in res]
    else:
        return []


def retry_rollback(f):
    def decorated(self, *args, **kwargs):
        try:
            result = f(self, *args, **kwargs)
        except psycopg2.errors.InFailedSqlTransaction:
            try:
                with db.transaction() as txn:
                    txn.rollback()
                logging.info("Rolled back failed transaction.")
            except InterfaceError:
                logging.info("Connection already closed.")
            result = f(self, *args, **kwargs)
        return result

    return decorated
