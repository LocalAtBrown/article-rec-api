from peewee import DecimalField, ForeignKeyField, TextField

from db.mappings.article import Article
from db.mappings.base import BaseMapping
from db.mappings.model import Model


class Rec(BaseMapping):
    class Meta:
        table_name = "recommendation"

    source_entity_id = TextField(null=False)
    model = ForeignKeyField(Model, null=False)
    recommended_article = ForeignKeyField(Article, null=False)
    score = DecimalField(max_digits=7, decimal_places=6)
