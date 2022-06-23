from peewee import SqliteDatabase

from db.mappings.base import db_proxy
from lib.config import config
from lib.db import db as PooledPostgresDB

if config.get("TEST_DB"):
    database = SqliteDatabase("/tmp/local.db")
else:
    database = PooledPostgresDB

db_proxy.initialize(database)
