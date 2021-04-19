from typing import Dict
from datetime import datetime, timezone, timedelta

from peewee import Model, DatabaseProxy
from playhouse.postgres_ext import DateTimeTZField as _DateTimeTZField

from playhouse.shortcuts import model_to_dict

db_proxy = DatabaseProxy()


def tzaware_now() -> datetime:
    return datetime.now(timezone.utc)


class DateTimeTZField(_DateTimeTZField):
    def db_value(self, value):
        if isinstance(value, datetime):
            return value.astimezone(timezone.utc)
        else:
            return datetime.fromisoformat(value).astimezone(timezone.utc)

    def python_value(self, value):
        if isinstance(value, datetime):
            return value.astimezone(timezone.utc)
        else:
            return datetime.fromisoformat(value).astimezone(timezone.utc)


class BaseMapping(Model):
    created_at = DateTimeTZField(null=False, default=tzaware_now)
    updated_at = DateTimeTZField(null=False, default=tzaware_now)

    class Meta:
        database = db_proxy

    def to_dict(self):
        resource = model_to_dict(self)
        resource = self.format_datetime(resource)
        return resource

    def format_datetime(self, resource: Dict) -> Dict:
        for key in resource.keys():
            if isinstance(resource[key], datetime):
                resource[key] = resource[key].isoformat()
            elif isinstance(resource[key], dict):
                resource[key] = self.format_datetime(resource[key])
        return resource
