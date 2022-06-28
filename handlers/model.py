import operator
from functools import reduce

import tornado.web
from peewee import DoesNotExist

from db.helpers import get_articles_by_external_ids, get_resource, retry_rollback
from db.mappings.model import Model
from db.mappings.recommendation import Rec
from handlers.base import APIHandler


class ModelArticleHandler(APIHandler):
    def __init__(self, *args, **kwargs):
        self.mapping = Model
        super(APIHandler, self).__init__(*args, **kwargs)

    @retry_rollback
    async def get(self, _id):
        model = None
        try:
            model = get_resource(self.mapping, _id)
        except DoesNotExist:
            raise tornado.web.HTTPError(404, "RESOURCE DOES NOT EXIST")

        rec_query = (
            Rec.select(Rec.source_entity_id)
            .join(Model, on=(Model.id == Rec.model))
            .where((Model.id == model["id"]))
            .distinct()
        )
        source_entity_ids = [rec.source_entity_id for rec in rec_query]
        articles = get_articles_by_external_ids(model["site"], source_entity_ids)
        res = {
            "results": articles,
        }
        self.api_response(res)


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

        if "site" in filters:
            clauses.append((self.mapping.site == filters["site"]))

        if len(clauses):
            conditional = reduce(operator.and_, clauses)
            query = query.where(conditional)

        return query

    @retry_rollback
    async def get(self):
        filters = self.get_arguments_as_dict()
        query = self.mapping.select()
        query = self.apply_conditions(query, **filters)
        query = self.apply_sort(query, **filters)
        res = {
            "results": [x.to_dict() for x in query],
        }
        self.api_response(res)
