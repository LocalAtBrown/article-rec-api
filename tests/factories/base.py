from copy import deepcopy
from db.helpers import create_resource, get_resource


class BaseFactory(object):
    @classmethod
    def create(cls, **kwargs) -> dict:
        params = cls.make_defaults()
        params.update(kwargs)
        resource_id = create_resource(cls.mapping, **params)
        instance = get_resource(cls.mapping, resource_id)
        return instance
