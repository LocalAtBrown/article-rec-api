from random import randint, random

from db.mappings.recommendation import Rec
from tests.factories.base import BaseFactory


class RecFactory(BaseFactory):
    mapping = Rec

    @classmethod
    def make_defaults(cls) -> dict:
        return {
            "source_entity_id": str(randint(1000, 9000)),
            "score": random(),
        }
