from random import randint, random

from tests.factories.base import BaseFactory
from db.mappings.recommendation import Rec


class RecFactory(BaseFactory):
    mapping = Rec
    defaults = {
        "source_entity_id": str(randint(1000, 9000)),
        "score": random(),
    }
