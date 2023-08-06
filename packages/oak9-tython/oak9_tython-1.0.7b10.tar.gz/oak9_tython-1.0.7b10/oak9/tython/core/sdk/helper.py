import re
from google.protobuf.any_pb2 import Any


def camel_to_snake(name):
    """
    Convert camelCase to snake_case
    """
    pattern = re.compile(r'(?<!^)(?=[A-Z])')
    snake_name = pattern.sub('_', name).lower()
    return snake_name


def snake_case_json(obj):
    """
    Recursively converts JSON attributes to snake_case
    """
    if isinstance(obj, dict):
        new_dict = {}
        for key, value in obj.items():
            new_key = camel_to_snake(key)
            new_value = snake_case_json(value)
            new_dict[new_key] = new_value
        return new_dict
    elif isinstance(obj, list):
        return [snake_case_json(item) for item in obj]
    else:
        return obj


def remove_attributes(data, prefix):
    """
    Recursively removes JSON attributes based on prefix
    """
    for key in list(data.keys()):
        if key.startswith(prefix):
            del data[key]
        elif isinstance(data[key], dict):
            remove_attributes(data[key], prefix)
        elif isinstance(data[key], list):
            for item in data[key]:
                if isinstance(item, dict):
                    remove_attributes(item, prefix)


def unpack_grpc_resource(data: Any, resource_type):
    """
    Unpacks grpc object
    """
    resource = resource_type()
    data.Unpack(resource)
    # resource.ParseFromString(data.value)
    return resource
