from peewee import SqliteDatabase

from db.mappings.base import db_proxy
from db.mappings.article import Article
from db.mappings.model import Model
from db.mappings.recommendation import Rec
from lib.db import db as PostgresDB
from lib.config import config

MAPPINGS = (Model, Article, Rec)


def recreate_tables(db):
    db.drop_tables(MAPPINGS)
    db.create_tables(MAPPINGS)


if config.get("TEST_DB"):
    database = SqliteDatabase("/tmp/local.db")
    db_proxy.initialize(database)
    recreate_tables(database)
else:
    db_proxy.initialize(PostgresDB)
