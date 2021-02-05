import functools

import tornado.testing
from tornado.concurrent import Future
from peewee import SqliteDatabase

from app import Application
from db.mappings import database
from db.mappings.model import Model
from db.mappings.article import Article
from db.mappings.recommendation import Rec


MAPPINGS = (Model, Article, Rec)


def recreate_tables(db):
    db.drop_tables(MAPPINGS)
    db.create_tables(MAPPINGS)


class BaseTest(tornado.testing.AsyncHTTPTestCase):
    def get_app(self):
        return Application()

    def stub_future(self, result=None):
        future = Future()
        future.set_result(result)

        return future

    def setUp(self):
        assert isinstance(database, SqliteDatabase), "database must be sqlite for tests"
        recreate_tables(database)
        super().setUp()
