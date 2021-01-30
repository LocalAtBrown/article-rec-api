from tests.factories.base import BaseFactory
from db.mappings.model import Model, Status


class ModelFactory(BaseFactory):
    mapping = Model
    defaults = {
        "type": Status.CURRENT.value,
    }
