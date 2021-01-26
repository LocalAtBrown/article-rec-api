import json
import logging
from typing import List

import tornado.web
from tornado.httputil import HTTPHeaders


class BaseHandler(tornado.web.RequestHandler):
    def initialize(self, *args, **kwargs):
        super(BaseHandler, self).initialize(*args, **kwargs)

    def on_connection_close(self):
        # There is no standard for client closed response codes,
        # nginx uses 499 which seems as reasonable as any other.
        self.set_status(499, "Client Closed Request")
        super(BaseHandler, self).on_connection_close()

    def set_default_headers(self):
        super(BaseHandler, self).set_default_headers()
        self.clear_header("Server")


class NotFoundHandler(BaseHandler):
    """Immediately raise a 404."""

    def prepare(self):
        super(NotFoundHandler, self).prepare()
        raise tornado.web.HTTPError(404)


class HealthHandler(BaseHandler):
    """Return 200 OK."""

    def get(self):
        self.finish("OK")


class APIHandler(BaseHandler):
    """Base class for API handlers."""

    def __init__(self, *args, **kwargs):
        self._json_body = None
        super(APIHandler, self).__init__(*args, **kwargs)

    def write_error(self, status_code, exc_info=None, **kwargs):
        """Write errors as a JSON response."""
        if not exc_info:
            logging.error("internal_error: no exception for error")
            msg = "INTERNAL_ERROR"
        else:
            _, error, _ = exc_info
            if isinstance(error, tornado.web.MissingArgumentError):
                msg = "MISSING_ARG_{}".format(error.arg_name.upper())
            elif isinstance(error, tornado.web.HTTPError):
                reason = "_".join(self._reason.upper().split())
                msg = error.log_message or reason or "INTERNAL_ERROR"
            else:
                logging.error("internal_error: %s", error)
                msg = "INTERNAL_ERROR"

        self.set_status(status_code)
        self.finish({"message": msg})

    @property
    def json_body(self):
        """Return parsed request body."""
        if self._json_body:
            return self._json_body

        content_type = self.request.headers.get("Content-Type", "text/plain")
        if not content_type.startswith("application/json"):
            raise tornado.web.HTTPError(415, "INVALID_CONTENT_TYPE")

        try:
            self._json_body = self.parse_json(self.request.body)
        except ValueError:
            raise tornado.web.HTTPError(400, "INVALID_JSON")

        return self._json_body

    def parse_json(self, body):
        return json.loads(body)
