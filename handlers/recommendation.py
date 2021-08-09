import operator
from datetime import datetime, timedelta
from functools import reduce
from random import randint
from typing import Dict

import tornado.web

from db.helpers import retry_rollback
from db.mappings.recommendation import Rec
from db.mappings.model import Model, Status, Type
from db.mappings.article import Article
from handlers.base import APIHandler


class DefaultRecs:
    STALE_AFTER_MIN = 5
    DEFAULT_TYPE = Type.POPULARITY.value
    _recs = None
    _last_updated = None

    @classmethod
    @retry_rollback
    def get_recs(cls):
        if cls.should_refresh():
            query = (
                Rec.select()
                .join(Model, on=(Model.id == Rec.model))
                .where(
                    (Model.type == cls.DEFAULT_TYPE)
                    & (Model.status == Status.CURRENT.value)
                )
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
        jitter_sec = randint(1, 30)
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
            clauses.append(
                (self.mapping.source_entity_id == filters["source_entity_id"])
            )

        if "exclude" in filters:
            query = query.join(
                Article, on=(Article.id == self.mapping.recommended_article)
            ).where((Article.external_id.not_in(filters["exclude"].split(","))))

        if "model_id" in filters:
            clauses.append((self.mapping.model_id == filters["model_id"]))

        elif "model_type" in filters:
            query = query.join(Model, on=(Model.id == self.mapping.model)).where(
                (Model.type == filters["model_type"])
                & (Model.status == Status.CURRENT.value)
            )

        if len(clauses):
            conditional = reduce(operator.and_, clauses)
            query = query.where(conditional)

        return query

    def validate_filters(self, **filters) -> Dict[str, str]:
        error_msgs = {}

        if "source_entity_id" in filters:
            try:
                int(filters["source_entity_id"])
            except:
                error_msgs[
                    "source_entity_id"
                ] = f"Invalid input syntax (int): {filters['source_entity_id']}"

        if "exclude" in filters:
            for exclude in filters["exclude"].split(","):
                try:
                    int(exclude)
                except:
                    error_msgs[
                        "exclude"
                    ] = f"Invalid input syntax (List[int]): {filters['exclude']}"

        if "model_id" in filters:
            try:
                int(filters["model_id"])
            except:
                error_msgs[
                    "model_id"
                ] = f"Invalid input syntax (int): {filters['model_id']}"

        elif "model_type" in filters:
            try:
                str(filters["model_type"])
            except:
                error_msgs[
                    "model_type"
                ] = f"Invalid input syntax (str): {filters['model_type']}"

        return error_msgs

    @retry_rollback
    async def get(self):
        filters = self.get_arguments()
        validation_errors = self.validate_filters(**filters)
        if validation_errors:
            raise tornado.web.HTTPError(status_code=400, log_message=validation_errors)
        query = self.mapping.select()
        query = self.apply_conditions(query, **filters)
        query = self.apply_sort(query, **filters)
        res = {
            "results": [x.to_dict() for x in query] or DefaultRecs.get_recs(),
        }
        self.api_response(res)
