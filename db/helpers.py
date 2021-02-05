from db.mappings.base import BaseMapping


def create_resource(mapping_class: BaseMapping, **params: dict) -> int:
    resource = mapping_class(**params)
    resource.save()
    return resource.id


def get_resource(mapping_class: BaseMapping, _id: int) -> dict:
    instance = mapping_class.get(mapping_class.id == _id)
    return instance.to_dict()
