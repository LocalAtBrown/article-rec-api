from tests.factories.base import BaseFactory
from db.mappings.model import Model, Type, Status
from lib.config import config

DEFAULT_SITE = config.get("DEFAULT_SITE")


class ModelFactory(BaseFactory):
    mapping = Model

    @classmethod
    def make_defaults(cls):
        return {
            "type": Type.ARTICLE.value,
            "status": Status.CURRENT.value,
            "site": DEFAULT_SITE,
        }
