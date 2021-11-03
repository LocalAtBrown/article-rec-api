from random import randint

from tests.factories.base import BaseFactory
from db.mappings.article import Article

DEFAULT_SITE = 'default_site'

class ArticleFactory(BaseFactory):
    mapping = Article

    @classmethod
    def make_defaults(cls):
        return {
            "external_id": str(randint(1000, 9000)),
            "site": DEFAULT_SITE,
        }
