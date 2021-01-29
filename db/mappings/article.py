import datetime

from peewee import TextField, DateTimeField, IntegerField

from db.mappings.base import BaseMapping


class Article(BaseMapping):
    class Meta:
        table_name = "article"

    external_id = IntegerField(null=False)
    title = TextField(null=False, default="")
    published_at = DateTimeField(null=True)
