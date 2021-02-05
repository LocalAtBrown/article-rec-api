import logging

import tornado.autoreload
import tornado.web

from handlers import recommendation, base
from lib.config import config


APP_SETTINGS = {
    "default_handler_class": base.NotFoundHandler,
    "debug": config.get("DEBUG"),
}


class Application(tornado.web.Application):
    def __init__(self):
        app_handlers = [
            (r"^/$", base.HealthHandler),
            (r"^/health/?$", base.HealthHandler),
            (r"^/recs/?$", recommendation.RecHandler),
        ]

        super(Application, self).__init__(app_handlers, **APP_SETTINGS)


if __name__ == "__main__":

    if config.get("DEBUG") is True:
        tornado.autoreload.start()

    logging_level = logging.getLevelName(config.get("LOG_LEVEL"))
    logging.getLogger().setLevel(logging_level)

    port = config.get("PORT")
    logging.info(f"service is listening on port {port}")

    http_server = tornado.httpserver.HTTPServer(request_callback=Application(), xheaders=True)
    http_server.listen(port)
    tornado.ioloop.IOLoop.current().start()
