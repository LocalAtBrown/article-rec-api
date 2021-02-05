from typing import Dict
import datetime

from peewee import Model, DateTimeField, DatabaseProxy
from playhouse.shortcuts import model_to_dict

db_proxy = DatabaseProxy()


class BaseMapping(Model):
    created_at = DateTimeField(null=False, default=datetime.datetime.now)
    updated_at = DateTimeField(null=False, default=datetime.datetime.now)

    class Meta:
        database = db_proxy

    def to_dict(self):
        resource = model_to_dict(self)
        resource = self.format_datetime(resource)
        return resource

    def format_datetime(self, resource: Dict) -> Dict:
        for key in resource.keys():
            if isinstance(resource[key], datetime.datetime):
                resource[key] = resource[key].isoformat()
            elif isinstance(resource[key], dict):
                resource[key] = self.format_datetime(resource[key])
        return resource
