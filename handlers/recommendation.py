import operator
from functools import reduce

from db.mappings.recommendation import Rec
from handlers.base import APIHandler

import datetime
import time
import json


def unix_time_ms(datetime_instance):
    return int(
        time.mktime(datetime_instance.timetuple()) * 1e3 + datetime_instance.microsecond / 1e3
    )


def datetime_serializer(obj):
    # TODO need to recursively serialize times on child fields
    if isinstance(obj, datetime.datetime):
        return int(unix_time_ms(obj) / 1000)  # unix seconds


class RecHandler(APIHandler):
    def __init__(self, *args, **kwargs):
        self.mapping = Rec
        super(APIHandler, self).__init__(*args, **kwargs)

    def apply_where_conditions(self, query, **filters):
        clauses = []

        if "model_id" in filters:
            clauses.append((self.mapping.model_id == filters["model_id"]))

        if "external_id" in filters:
            clauses.append((self.mapping.model_id == filters["external_id"]))

        if "id" in filters:
            clauses.append((self.mapping.id == filters["id"]))

        if len(clauses):
            conditional = reduce(operator.and_, clauses)
            query = query.where(conditional)

        return query

    async def get(self):
        filters = {k: self.get_argument(k) for k in self.request.arguments}
        query = self.mapping.select()
        query = self.apply_where_conditions(query, **filters)
        # res = query.order_by(-self.mapping.score)
        recs = [x.to_dict() for x in query]

        res = {"results": recs}
        data = json.dumps(res, default=datetime_serializer)
        self.finish(data)
