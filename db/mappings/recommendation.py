from peewee import TextField, DecimalField, ForeignKeyField

from db.mappings.base import BaseMapping
from db.mappings.model import Model
from db.mappings.article import Article


class Rec(BaseMapping):
    class Meta:
        table_name = "recommendation"

    source_entity_id = TextField(null=False)
    model = ForeignKeyField(Model, null=False)
    recommended_article = ForeignKeyField(Article, null=False)
    score = DecimalField(max_digits=7, decimal_places=6)
