import datetime

from peewee import TextField, DateTimeField, IntegerField

from db.mappings.base import BaseMapping


class Article(BaseMapping):
    class Meta:
        table_name = "article"

    external_id = TextField(null=False, default="")
    title = TextField(null=False, default="")
    path = TextField(null=False, default="")
    published_at = DateTimeField(null=True)
    site = TextField(null=False)
