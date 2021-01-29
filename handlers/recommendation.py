import operator
from functools import reduce
from decimal import Decimal

from db.mappings.recommendation import Rec
from handlers.base import APIHandler
from db.mappings.model import Model, Status

import datetime
import time
import json


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


class RecHandler(APIHandler):
    def __init__(self, *args, **kwargs):
        self.mapping = Rec
        super(APIHandler, self).__init__(*args, **kwargs)

    def apply_conditions(self, query, **filters):
        clauses = []

        if "source_entity_id" in filters:
            clauses.append((self.mapping.source_entity_id == filters["source_entity_id"]))

        if "model_id" in filters:
            clauses.append((self.mapping.model_id == filters["model_id"]))
        elif "model_type" in filters:
            query = query.join(Model).where(
                (Model.type == filters["model_type"]) & (Model.status == Status.CURRENT.value)
            )

        if len(clauses):
            conditional = reduce(operator.and_, clauses)
            query = query.where(conditional)

        if "sort_by" in filters:
            sort_by_field = getattr(self.mapping, filters["sort_by"])
            order_by_rule = sort_by_field.desc
            if "order_by" in filters:
                order_by_rule = getattr(sort_by_field, filters["order_by"])
            query = query.order_by(order_by_rule())

        return query

    async def get(self):
        filters = {k: self.get_argument(k) for k in self.request.arguments}
        query = self.mapping.select()
        query = self.apply_conditions(query, **filters)
        recs = [x.to_dict() for x in query]
        res = {"results": recs}
        data = json.dumps(res, default=default_serializer)
        self.finish(data)
