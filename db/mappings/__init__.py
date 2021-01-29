from peewee import SqliteDatabase

from db.mappings.base import db_proxy
from lib.db import db as PostgresDB
from lib.config import config


if config.get("TEST_DB"):
    database = SqliteDatabase("/tmp/local.db")
else:
    database = PostgresDB

db_proxy.initialize(database)
