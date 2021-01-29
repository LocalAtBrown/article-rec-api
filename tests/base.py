import tornado.testing
from tornado.concurrent import Future

from app import Application


class BaseTest(tornado.testing.AsyncHTTPTestCase):
    def get_app(self):
        return Application()

    def stub_future(self, result=None):
        future = Future()
        future.set_result(result)

        return future
