from datetime import datetime, timedelta
import operator
from functools import reduce
from random import randint

from db.mappings.recommendation import Rec
from handlers.base import APIHandler
from db.mappings.model import Model, Status, Type
from db.mappings.article import Article


class DefaultRecs:
    STALE_AFTER_MIN = 5
    DEFAULT_TYPE = Type.POPULARITY.value
    _recs = None
    _last_updated = None

    @classmethod
    def get_recs(cls):
        if cls.should_refresh():
            query = (
                Recs.select()
                .join(Model, on=(Model.id == Rec.model))
                .where((Model.type == DEFAULT_TYPE) & (Model.status == Status.CURRENT.value))
                .order_by(Rec.score.desc())
            )
            cls._recs = [x.to_dict() for x in query]
            cls._last_updated = datetime.now()

        return cls._recs

    @classmethod
    def should_refresh(cls):
        if not cls._recs:
            return True
        # add random jitter to prevent multiple unneeded db hits at the same time
        jitter_sec = randint(30)
        stale_threshold = datetime.now() - timedelta(
            minutes=cls.STALE_AFTER_MIN, seconds=jitter_sec
        )
        if cls._last_updated < stale_threshold:
            return True
        return False


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
            "results": [x.to_dict() for x in query] or DefaultRecs.get_recs(),
        }
        self.api_response(res)
