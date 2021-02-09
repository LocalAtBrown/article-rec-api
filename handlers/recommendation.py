import operator
from functools import reduce

from db.mappings.recommendation import Rec
from handlers.base import APIHandler
from db.mappings.model import Model, Status
from db.mappings.article import Article


class RecHandler(APIHandler):
    def __init__(self, *args, **kwargs):
        self.mapping = Rec
        super(APIHandler, self).__init__(*args, **kwargs)

    def apply_conditions(self, query, **filters):
        clauses = []

        if "source_entity_id" in filters:
            clauses.append((self.mapping.source_entity_id == filters["source_entity_id"]))

        if "exclude" in filters:
            query = query.join(Article, on=(Article.id == self.mapping.recommended_article)).where(
                (Article.external_id.not_in(filters["exclude"].split(",")))
            )

        if "model_id" in filters:
            clauses.append((self.mapping.model_id == filters["model_id"]))
        elif "model_type" in filters:
            query = query.join(Model, on=(Model.id == self.mapping.model)).where(
                (Model.type == filters["model_type"]) & (Model.status == Status.CURRENT.value)
            )

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
