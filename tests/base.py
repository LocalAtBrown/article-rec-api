import functools

import tornado.testing
from tornado.concurrent import Future

from app import Application
from db.mappings import database


class BaseTest(tornado.testing.AsyncHTTPTestCase):
    def get_app(self):
        return Application()

    def stub_future(self, result=None):
        future = Future()
        future.set_result(result)

        return future


def rollback_db(fn):
    @functools.wraps(fn)
    @tornado.testing.gen_test
    def wrapper(self, *args, **kwargs):
        db_conn = database.connection()

        def execute_sql(sql, params=None, require_commit=True):
            with db_conn.cursor() as cursor:
                cursor.execute(sql, params or ())
            return cursor

        _execute_sql = database.execute_sql
        database.execute_sql = execute_sql

        try:
            yield fn(self, *args, **kwargs)
        except:
            raise
        finally:
            database.execute_sql = _execute_sql

            db_conn.rollback()
            db_conn.close()

    return wrapper
