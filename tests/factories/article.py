from random import randint

from tests.factories.base import BaseFactory
from db.mappings.article import Article


class ArticleFactory(BaseFactory):
    mapping = Article
    defaults = {
        "external_id": str(randint(1000, 9000)),
    }
