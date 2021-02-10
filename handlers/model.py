import operator
from functools import reduce

from handlers.base import APIHandler
from db.mappings.model import Model, Status
from db.helpers import update_resource, get_resource


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

    async def patch(self, resource_id):
        # TODO if a new current model is specified,
        # add logic to reset old current model to stale
        # TODO add @admin wrapper
        # TODO move generalized logic into parent class
        update_resource(self.mapping, resource_id, **self.json_body)
        resource = get_resource(self.mapping, resource_id)
        self.api_response(resource)
