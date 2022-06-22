from random import randint

from db.mappings.article import Article
from lib.config import config
from tests.factories.base import BaseFactory

DEFAULT_SITE = config.get("DEFAULT_SITE")


class ArticleFactory(BaseFactory):
    mapping = Article

    @classmethod
    def make_defaults(cls):
        return {
            "external_id": str(randint(1000, 9000)),
            "site": DEFAULT_SITE,
        }
