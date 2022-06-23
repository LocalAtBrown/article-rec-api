from db.mappings.model import Model, Status, Type
from lib.config import config
from tests.factories.base import BaseFactory

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
