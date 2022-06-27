import logging
import operator
from datetime import datetime, timedelta
from functools import reduce
from random import randint
from typing import Any, Dict, List, Optional

import tornado.web
from cachetools import TTLCache, cached, keys

from db.helpers import retry_rollback
from db.mappings.article import Article
from db.mappings.model import Model, Status, Type
from db.mappings.recommendation import Rec
from handlers.base import APIHandler
from lib.config import config

MAX_PAGE_SIZE = config.get("MAX_PAGE_SIZE")
DEFAULT_SITE = config.get("DEFAULT_SITE")
STALE_AFTER_MIN = 15
# each result takes roughly 50,000 bytes; 2048 cached results ~= 100 MBs
TTL_CACHE: TTLCache = TTLCache(maxsize=2048, ttl=STALE_AFTER_MIN * 60)
# counter of default recs served for site
DEFAULT_REC_COUNTER: Dict[str, int] = {}
# counter of db hits by site
DB_HIT_COUNTER: Dict[str, int] = {}
# counter of all handled requests by site
TOTAL_HANDLED: Dict[str, int] = {}


def incr_metric_total(counter: Dict[str, int], site: str) -> None:
    """
    increment running metric totals to be flushed on an interval
    """
    if counter.get(site):
        counter[site] += 1
    else:
        counter[site] = 1


def instance_unaware_key(instance, *args, **kwargs):
    # ignore "self" argument
    key = keys.hashkey(*args, **kwargs)
    return key


class DefaultRecs:
    DEFAULT_TYPE = Type.POPULARITY.value
    _recs: dict[str, list[dict]] = {}
    _last_updated: dict[str, datetime] = {}

    @classmethod
    @retry_rollback
    def get_recs(cls, site: str, external_id: str, size: int) -> List[Dict[str, Any]]:
        incr_metric_total(DEFAULT_REC_COUNTER, site)
        logging.info(f"Returning default recs for site:{site}, external_id:{external_id}")

        if cls.should_refresh(site):
            query = (
                Rec.select()
                .join(Model, on=(Model.id == Rec.model))
                .where((Model.type == cls.DEFAULT_TYPE) & (Model.status == Status.CURRENT.value))
                .order_by(Rec.score.desc())
            )
            if site:
                query = query.join(Article, on=(Article.id == Rec.recommended_article)).where(Article.site == site)

            cls._recs[site] = [x.to_dict() for x in query]
            cls._last_updated[site] = datetime.now()

        recs = cls._recs[site]
        return recs[:size]

    @classmethod
    def should_refresh(cls, site):
        if not cls._recs.get(site):
            return True
        # add random jitter to prevent multiple unneeded db hits at the same time
        jitter_sec = randint(1, 30)
        stale_threshold = datetime.now() - timedelta(minutes=STALE_AFTER_MIN, seconds=jitter_sec)
        # Note None is always less than stale_threshold
        if cls._last_updated.get(site) < stale_threshold:
            return True
        return False


class RecHandler(APIHandler):
    def __init__(self, *args, **kwargs):
        self.mapping = Rec
        super(APIHandler, self).__init__(*args, **kwargs)

    def apply_conditions(self, query, **filters):
        clauses = []

        if filters.get("source_entity_id"):
            clauses.append((self.mapping.source_entity_id == filters["source_entity_id"]))

        article_clauses = []
        if filters.get("exclude"):
            article_clauses.append((Article.external_id.not_in(filters["exclude"].split(","))))

        if filters.get("site"):
            article_clauses.append((Article.site == filters["site"]))

        if article_clauses:
            query = query.join(Article, on=(Article.id == self.mapping.recommended_article)).where(
                reduce(operator.and_, article_clauses)
            )

        if filters.get("model_id"):
            clauses.append((self.mapping.model_id == filters["model_id"]))

        elif filters.get("model_type"):
            query = query.join(Model, on=(Model.id == self.mapping.model)).where(
                (Model.type == filters["model_type"]) & (Model.status == Status.CURRENT.value)
            )

        if filters.get("size"):
            query = query.limit(filters["size"])

        if len(clauses):
            conditional = reduce(operator.and_, clauses)
            query = query.where(conditional)

        return query

    def validate_filters(self, **filters) -> Dict[str, str]:
        error_msgs = {}

        if "exclude" in filters:
            for exclude in filters["exclude"].split(","):
                try:
                    int(exclude)
                except ValueError:
                    return f"Invalid input for 'exclude' (List[int]): {filters['exclude']}"

        if "model_id" in filters:
            try:
                int(filters["model_id"])
            except ValueError:
                return f"Invalid input for 'model_id' (int): {filters['model_id']}"

        if "size" in filters:
            try:
                assert int(filters["size"]) < MAX_PAGE_SIZE
            except (ValueError, AssertionError):
                return f"Invalid input for 'size' (int), must be below {MAX_PAGE_SIZE}: {filters['size']}"

        return error_msgs

    @cached(cache=TTL_CACHE, key=instance_unaware_key)
    def fetch_cached_results(
        self,
        source_entity_id: Optional[str] = None,
        site: Optional[str] = None,
        model_type: Optional[str] = None,
        model_id: Optional[str] = None,
        exclude: Optional[str] = None,
        size: Optional[str] = None,
        sort_by: Optional[str] = None,
        order_by: Optional[str] = None,
    ):
        filters = locals()
        filters.pop("self")
        query = self.mapping.select()
        query = self.apply_conditions(query, **filters)
        query = self.apply_sort(query, **filters)
        incr_metric_total(DB_HIT_COUNTER, site)
        return [x.to_dict() for x in query]

    def fetch_results(self, **filters: Dict[str, str]) -> List[Rec]:
        results = self.fetch_cached_results(
            source_entity_id=filters.get("source_entity_id"),
            site=filters.get("site"),
            model_type=filters.get("model_type"),
            model_id=filters.get("model_id"),
            exclude=filters.get("exclude"),
            size=filters.get("size"),
            sort_by=filters.get("sort_by"),
            order_by=filters.get("order_by"),
        )
        return results

    @retry_rollback
    async def get(self):
        filters = self.get_arguments()
        filters["site"] = filters.get("site", DEFAULT_SITE)
        validation_errors = self.validate_filters(**filters)
        if validation_errors:
            raise tornado.web.HTTPError(status_code=400, log_message=validation_errors)

        res = {
            "results": self.fetch_results(**filters)
            or DefaultRecs.get_recs(filters["site"], filters.get("source_entity_id"), int(filters["size"])),
        }
        incr_metric_total(TOTAL_HANDLED, filters["site"])
        self.api_response(res)
