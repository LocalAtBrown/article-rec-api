import datetime
import time
import json
import logging
from typing import List
from decimal import Decimal

import tornado.web
from tornado.httputil import HTTPHeaders


def unix_time_ms(datetime_instance):
    return int(
        time.mktime(datetime_instance.timetuple()) * 1e3 + datetime_instance.microsecond / 1e3
    )


def default_serializer(obj):
    if isinstance(obj, datetime.datetime):
        return int(unix_time_ms(obj) / 1000)  # unix seconds
    if isinstance(obj, Decimal):
        return str(obj)
    raise TypeError(f"couldn't serialize obj: {obj}")


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
        super(APIHandler, self).__init__(*args, **kwargs)

    def get_arguments(self):
        return {k: self.get_argument(k) for k in self.request.arguments}

    def apply_sort(self, query, **filters):
        DEFAULT_ORDER_BY = "desc"
        if "sort_by" in filters:
            sort_by_field = getattr(self.mapping, filters["sort_by"], None)
            if not sort_by_field:
                return query
            default_order_rule = getattr(sort_by_field, DEFAULT_ORDER_BY)
            order_by_rule = getattr(
                sort_by_field, filters.get("order_by", DEFAULT_ORDER_BY), default_order_rule
            )
            query = query.order_by(order_by_rule())

        return query

    def apply_conditions(self, query, **filters):
        """override for custom where logic"""
        raise NotImplementedError

    def api_response(self, data, code=200):
        self.set_status(code)
        self.set_header("Content-Type", "application/json")
        self.add_header("Access-Control-Allow-Origin", "https://washingtoncitypaper.com")
        self.add_header("Access-Control-Allow-Headers", "Content-Type, Authorization")

        if not 200 <= code < 300:
            response = {"message": data}
        if not isinstance(data, str):
            response = json.dumps(data, default=default_serializer)
        self.finish(response)

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
