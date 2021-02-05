from tests.factories.base import BaseFactory
from db.mappings.model import Model, Type, Status


class ModelFactory(BaseFactory):
    mapping = Model

    @classmethod
    def make_defaults(cls):
        return {
            "type": Type.ARTICLE.value,
            "status": Status.CURRENT.value,
        }
