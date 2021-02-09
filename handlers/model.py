import operator
from functools import reduce

from handlers.base import APIHandler
from db.mappings.model import Model, Status


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
