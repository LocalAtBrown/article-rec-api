import logging
import asyncio

import tornado.autoreload
import tornado.web

from handlers import recommendation, base, model
from lib.config import config
from lib.metrics import write_aggregate_metrics, Unit


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
            (r"^/models/?$", model.ModelHandler),
            (r"^/models/(\d+)/set_current/?", model.ModelHandler),
            (r"^/models/(\d+)/articles/?", model.ModelArticleHandler),
        ]

        super(Application, self).__init__(app_handlers, **APP_SETTINGS)


async def write_latency_metrics():
    INTERVAL_MIN = 1
    while True:
        await asyncio.sleep(INTERVAL_MIN * 60)
        latencies = base.LatencyBuffer.flush()
        if latencies:
            write_aggregate_metrics(
                "aggregate_latency", latencies, unit=Unit.MILLISECONDS
            )


if __name__ == "__main__":
    if config.get("DEBUG") is True:
        tornado.autoreload.start()

    logging_level = logging.getLevelName(config.get("LOG_LEVEL"))
    logging.getLogger().setLevel(logging_level)

    port = config.get("PORT")
    logging.info(f"service is listening on port {port}")

    http_server = tornado.httpserver.HTTPServer(
        request_callback=Application(), xheaders=True
    )
    http_server.listen(port)
    io_loop = tornado.ioloop.IOLoop.current()
    io_loop.add_callback(write_latency_metrics)
    io_loop.start()
