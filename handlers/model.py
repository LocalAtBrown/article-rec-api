import operator
import tornado.web

from functools import reduce
from peewee import DoesNotExist

from db.helpers import get_resource, retry_rollback
from db.mappings.model import Model
from handlers.base import APIHandler, admin_only


class ModelHandler(APIHandler):
    def __init__(self, *args, **kwargs):
        self.mapping = Model
        super(APIHandler, self).__init__(*args, **kwargs)

    def apply_conditions(self, query, **filters):
        clauses = []

        if "status" in filters:
            clauses.append((self.mapping.status == filters["status"]))

        if "type" in filters:
            clauses.append((self.mapping.type == filters["type"]))

        if len(clauses):
            conditional = reduce(operator.and_, clauses)
            query = query.where(conditional)

        return query

    @retry_rollback
    async def get(self):
        filters = self.get_arguments()
        query = self.mapping.select()
        query = self.apply_conditions(query, **filters)
        query = self.apply_sort(query, **filters)
        res = {
            "results": [x.to_dict() for x in query],
        }
        self.api_response(res)

    @admin_only
    async def patch(self, _id):
        try:
            resource = get_resource(self.mapping, _id)
        except DoesNotExist:
            raise tornado.web.HTTPError(404, "RESOURCE DOES NOT EXIST")
        self.mapping.set_current(_id, resource["type"])
        resource = get_resource(self.mapping, _id)
        self.api_response(resource)
