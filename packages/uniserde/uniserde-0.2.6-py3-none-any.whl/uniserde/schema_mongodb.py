import inspect
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, Literal, Type, Union, get_args, get_type_hints

from bson import ObjectId

from . import serde_class
from .common import *


def make_schema_bool_to_bool(
    none: None,
    value_type: Type,
    recur: Recur,
):
    return {"type": "boolean"}


def make_schema_int_to_int(
    none: None,
    value_type: Type,
    recur: Recur,
):
    return {"bsonType": ["int", "long"]}


def make_schema_float_to_float(
    none: None,
    value_type: Type,
    recur: Recur,
):
    return {"bsonType": ["int", "long", "double"]}


def make_schema_bytes_to_bytes(
    none: None,
    value_type: Type,
    recur: Recur,
):
    return {"bsonType": "binData"}


def make_schema_str_to_str(
    none: None,
    value_type: Type,
    recur: Recur,
):
    return {"type": "string"}


def make_schema_datetime_to_datetime(
    none: None,
    value_type: Type,
    recur: Recur,
):
    return {"bsonType": "date"}


def make_schema_list_to_list(
    none: None,
    value_type: Type,
    recur: Recur,
):
    return {
        "type": "array",
        "items": recur(None, get_args(value_type)[0]),
    }


def make_schema_dict_to_dict(
    none: None,
    value_type: Type,
    recur: Recur,
):
    subtypes = get_args(value_type)
    assert subtypes[0] is str, value_type

    return {
        "type": "object",
        "items": recur(None, subtypes[1]),
    }


def make_schema_object_id_to_object_id(
    none: None,
    value_type: Type,
    recur: Recur,
):
    return {"bsonType": "objectId"}


def make_schema_literal_to_str(
    none: None,
    value_type: Type,
    recur: Recur,
):
    return {"type": "string"}


def make_schema_union(
    none: None,
    value_type: Type,
    recur: Recur,
):
    # Convert each subtype to a BSON schema
    sub_schemas = []
    for subtype in get_args(value_type):
        # Union is used by Python to represent "Optional"
        if subtype is type(None):
            sub_schemas.append({"type": "null"})
            continue

        sub_schemas.append(recur(None, subtype))

    # Prettify the result: instead of `{anyof {type ...} {type ...}}` just
    # create one `type`
    types = []
    bson_types = []
    others = []

    for schema in sub_schemas:
        if len(schema) == 1:

            # Standard Json Schema type
            try:
                type_field = schema["type"]
            except KeyError:
                pass
            else:
                if isinstance(type_field, list):
                    types.extend(type_field)
                else:
                    types.append(type_field)

                continue

            # BSON type
            try:
                type_field = schema["bsonType"]
            except KeyError:
                pass
            else:
                if isinstance(type_field, list):
                    bson_types.extend(type_field)
                else:
                    bson_types.append(type_field)

                continue

        # General case
        others.append(schema)

    # Create new, merged schemas
    sub_schemas = []

    if bson_types:
        sub_schemas.append({"bsonType": types + bson_types})
    elif types:
        sub_schemas.append({"type": types})

    sub_schemas.extend(others)

    if len(sub_schemas) == 1:
        return sub_schemas[0]

    return {"anyOf": sub_schemas}


def make_schema_any(
    none: None,
    value_type: Type,
    recur: Recur,
):
    return {}


def make_schema_tuple_to_list(
    none: None,
    value_type: Type,
    recur: Recur,
):
    return {
        "type": "array",
        "items": [recur(None, subtype) for subtype in get_args(value_type)],
    }


def make_schema_set_to_list(
    none: None,
    value_type: Type,
    recur: Recur,
):
    return {
        "type": "array",
        "items": recur(None, get_args(value_type)[0]),
    }


def create_class_schema_ignore_serialize_as_child(value_type: Type, recur: Recur):
    doc_field_names = []
    doc_properties = {}
    result = {
        "type": "object",
        "properties": doc_properties,
        "additionalProperties": False,
    }

    for field_py_name, field_type in get_type_hints(value_type).items():
        field_doc_name = all_lower_to_camel_case(field_py_name)

        if field_py_name == "id":
            field_doc_name = "_id"

        doc_field_names.append(field_doc_name)
        doc_properties[field_doc_name] = recur(None, field_type)

    # The `required` field may only be present if it contains at least one value
    if doc_field_names:
        result["required"] = doc_field_names

    return result


def make_schema_class(
    none: None,
    value_type: Type,
    recur: Recur,
):
    assert inspect.isclass(value_type), value_type

    # Case: The class has a custom schema method
    try:
        override_method = getattr(value_type, "as_mongodb_schema")
    except AttributeError:
        pass
    else:
        if override_method.__func__ is not serde_class.Serde.as_mongodb_schema.__func__:
            return override_method()

    # Case: Enum
    if issubclass(value_type, Enum):
        return {
            "enum": [all_upper_to_camel_case(variant.name) for variant in value_type],
        }

    # Case: Class, and definitely not one of it's children
    if not should_serialize_as_child(value_type):
        return create_class_schema_ignore_serialize_as_child(value_type, recur)

    # Case: Class or one of its children

    # Create the schemas for all allowable classes
    sub_schemas = []
    for subtype in all_subclasses(value_type, True):
        schema = create_class_schema_ignore_serialize_as_child(subtype, recur)
        assert schema["type"] == "object", schema

        schema["properties"]["type"] = {
            "enum": [upper_camel_case_to_camel_case(subtype.__name__)]
        }

        required = schema.setdefault("required", [])
        required.insert(0, "type")

        sub_schemas.append(schema)

    # Create the final, combined schema
    if len(sub_schemas) == 1:
        return sub_schemas[0]
    else:
        return {"anyOf": sub_schemas}


SCHEMA_MAKERS: Dict[Type, Serializer] = {
    bool: make_schema_bool_to_bool,
    int: make_schema_int_to_int,
    float: make_schema_float_to_float,
    bytes: make_schema_bytes_to_bytes,
    str: make_schema_str_to_str,
    datetime: make_schema_datetime_to_datetime,
    list: make_schema_list_to_list,
    dict: make_schema_dict_to_dict,
    Union: make_schema_union,
    Any: make_schema_any,
    ObjectId: make_schema_object_id_to_object_id,
    Literal: make_schema_literal_to_str,
    tuple: make_schema_tuple_to_list,
    set: make_schema_set_to_list,
}


def as_mongodb_schema(
    value_type: Type,
    *,
    custom_handlers: Dict[Type, Callable[[Any], Any]] = {},
) -> Any:
    return common_serialize(
        None,
        value_type,
        make_schema_class,
        SCHEMA_MAKERS,
        custom_handlers,
    )
