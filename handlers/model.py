import operator
from functools import reduce

from handlers.base import APIHandler, admin_only
from db.mappings.model import Model, Status
from db.helpers import get_resource


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
        resource = get_resource(self.mapping, _id)
        self.mapping.set_current(_id, resource["type"])
        resource = get_resource(self.mapping, _id)
        self.api_response(resource)
