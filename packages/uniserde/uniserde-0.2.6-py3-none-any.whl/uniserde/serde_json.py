import base64
import inspect
import typing
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Literal, Tuple, Type, Union

import dateutil.parser
from bson import ObjectId

from . import serde_class
from .common import *

__all__ = [
    "as_json",
    "from_json",
    "Jsonable",
]


Jsonable = Union[
    None,
    bool,
    int,
    float,
    str,
    Dict[str, "Jsonable"],
    List["Jsonable"],
    Tuple["Jsonable", ...],
]


def serialize_bool_to_bool(
    value: Any,
    value_type: Type,
    recur: Recur,
) -> bool:
    assert isinstance(value, bool), value
    return value


def serialize_int_to_int(
    value: Any,
    value_type: Type,
    recur: Recur,
) -> int:
    assert isinstance(value, int), value
    return value


def serialize_float_to_float(
    value: Any,
    value_type: Type,
    recur: Recur,
) -> float:
    assert isinstance(value, (int, float)), value
    return float(value)


def serialize_bytes_to_str(
    value: Any,
    value_type: Type,
    recur: Recur,
) -> str:
    assert isinstance(value, bytes), value
    return base64.b64encode(value).decode("utf-8")


def serialize_str_to_str(
    value: Any,
    value_type: Type,
    recur: Recur,
) -> str:
    assert isinstance(value, str), value
    return value


def serialize_datetime_to_str(
    value: Any,
    value_type: Type,
    recur: Recur,
) -> str:
    assert isinstance(value, datetime), value
    assert (
        value.tzinfo is not None
    ), f"Encountered datetime without a timezone. Please always set timezones, or expect hard to find bugs."
    return value.isoformat()


def serialize_list_to_list(
    value: Any,
    value_type: Type,
    recur: Recur,
) -> List[Any]:
    assert isinstance(value, list), value
    return [recur(v, typing.get_args(value_type)[0]) for v in value]


def serialize_dict_to_dict(
    value: Any,
    value_type: Type,
    recur: Recur,
) -> Dict[Any, Any]:
    subtypes = typing.get_args(value_type)
    assert isinstance(value, dict), value
    return {recur(k, subtypes[0]): recur(v, subtypes[1]) for k, v in value.items()}


def serialize_object_id_to_str(
    value: Any,
    value_type: Type,
    recur: Recur,
) -> str:
    assert isinstance(value, ObjectId), value
    return str(value)


def serialize_optional(
    value: Any,
    value_type: Type,
    recur: Recur,
) -> Any:
    if value is None:
        return None

    return recur(value, typing.get_args(value_type)[0])


def serialize_any(
    value: Any,
    value_type: Type,
    recur: Recur,
) -> Any:
    return value


def serialize_literal_as_is(
    value: Any,
    value_type: Type,
    recur: Recur,
) -> Any:
    assert isinstance(value, str), value
    return value


def serialize_tuple_as_list(
    value: Any,
    value_type: Type,
    recur: Recur,
) -> List[Any]:
    assert isinstance(value, tuple), value
    subtypes = typing.get_args(value_type)
    assert len(subtypes) == len(value), (subtypes, value)

    return [recur(v, subtype) for v, subtype in zip(value, subtypes)]


def serialize_set_as_list(
    value: Any,
    value_type: Type,
    recur: Recur,
) -> List[Any]:
    assert isinstance(value, set), value
    subtype = typing.get_args(value_type)[0]
    return [recur(v, subtype) for v in value]


def serialize_class(
    value: Any,
    value_type: Type,
    recur: Recur,
) -> Any:
    assert inspect.isclass(value_type), value_type

    # Case: The class has a custom serialization method
    try:
        override_method = getattr(value, "as_json")
    except AttributeError:
        pass
    else:
        if override_method.__func__ is not serde_class.Serde.as_json:
            return override_method()

    # Case: Enum
    if issubclass(value_type, Enum):
        assert isinstance(value, value_type), value
        return all_upper_to_camel_case(value.name)

    # Case: Anything else
    # Make sure to serialize as the correct class
    if should_serialize_as_child(value_type):
        assert issubclass(type(value), value_type), (type(value), value_type)
        value_type = type(value)

    result = {}
    for field_py_name, field_type in typing.get_type_hints(value_type).items():
        field_doc_name = all_lower_to_camel_case(field_py_name)
        result[field_doc_name] = recur(getattr(value, field_py_name), field_type)

    # Add a type tag?
    if should_serialize_as_child(value_type):
        result["type"] = upper_camel_case_to_camel_case(value.__class__.__name__)

    return result


JSON_SERIALIZERS: Dict[Type, Serializer] = {
    bool: serialize_bool_to_bool,
    int: serialize_int_to_int,
    float: serialize_float_to_float,
    bytes: serialize_bytes_to_str,
    str: serialize_str_to_str,
    datetime: serialize_datetime_to_str,
    list: serialize_list_to_list,
    dict: serialize_dict_to_dict,
    Union: serialize_optional,
    Any: serialize_any,
    ObjectId: serialize_object_id_to_str,
    Literal: serialize_literal_as_is,
    tuple: serialize_tuple_as_list,
    set: serialize_set_as_list,
}


def as_json(
    value: Any,
    *,
    as_type: Optional[Type] = None,
    custom_serializers: Dict[Type, Callable[[Any], Any]] = {},
) -> Jsonable:
    return common_serialize(
        value,
        type(value) if as_type is None else as_type,
        serialize_class,
        JSON_SERIALIZERS,
        custom_serializers,
    )


def deserialize_bool_from_bool(
    value: Any,
    value_type: Type,
    recur: Recur,
) -> bool:
    if not isinstance(value, bool):
        raise SerdeError(f"Expected bool, got {value}")

    return value


def deserialize_int_from_int(
    value: Any,
    value_type: Type,
    recur: Recur,
) -> int:
    if not isinstance(value, (float, int)) or int(value) != value:
        raise SerdeError(f"Expected int, got {value}")

    return int(value)


def deserialize_float_from_float(
    value: Any,
    value_type: Type,
    recur: Recur,
) -> float:
    if not isinstance(value, (int, float)):
        raise SerdeError(f"Expected float, got {value}")

    return float(value)


def deserialize_bytes_from_str(
    value: Any,
    value_type: Type,
    recur: Recur,
) -> bytes:
    if not isinstance(value, str):
        raise SerdeError(f"Expected bytes encoded as string, got {value}")

    try:
        return base64.b64decode(value.encode("utf-8"))
    except ValueError:
        raise SerdeError("Received invalid base64 encoded string.")


def deserialize_str_from_str(
    value: Any,
    value_type: Type,
    recur: Recur,
) -> str:
    if not isinstance(value, str):
        raise SerdeError(f"Expected string, got {value}")

    return value


def deserialize_datetime_from_str(
    value: Any,
    value_type: Type,
    recur: Recur,
) -> datetime:
    if not isinstance(value, str):
        raise SerdeError(f"Expected date/time string, got {value}")

    try:
        result = dateutil.parser.isoparse(value)
    except ValueError:
        raise SerdeError(f"Expected date/time, got {value}") from None

    if result.tzinfo is None:
        raise SerdeError(f"The date/time value {value} is missing a timezone.")

    return result


def deserialize_list_from_list(
    value: Any,
    value_type: Type,
    recur: Recur,
) -> List[Any]:
    if not isinstance(value, list):
        raise SerdeError(f"Expected list, got {value}")

    subtype = typing.get_args(value_type)[0]

    return [recur(v, subtype) for v in value]


def deserialize_dict_from_dict(
    value: Any,
    value_type: Type,
    recur: Recur,
) -> Dict[Any, Any]:
    if not isinstance(value, dict):
        raise SerdeError(f"Expected dict, got {value}")

    subtypes = typing.get_args(value_type)

    return {recur(k, subtypes[0]): recur(v, subtypes[1]) for k, v in value.items()}


def deserialize_object_id_from_str(
    value: Any,
    value_type: Type,
    recur: Recur,
) -> ObjectId:
    if not isinstance(value, str):
        raise SerdeError(f"Expected ObjectId string, got {value}")

    try:
        result = ObjectId(value)
    except ValueError:
        raise SerdeError(f"Expected ObjectId string, got {value}") from None

    return result


def deserialize_optional(
    value: Any,
    value_type: Type,
    recur: Recur,
) -> Any:
    if value is None:
        return None

    return recur(value, typing.get_args(value_type)[0])


def deserialize_any(
    value: Any,
    value_type: Type,
    recur: Recur,
) -> Any:
    return value


def deserialize_literal_as_is(
    value: Any,
    value_type: Type,
    recur: Recur,
) -> Any:
    options = typing.get_args(value_type)
    if value not in options:
        raise SerdeError(f"Expected {value_type}, got {value}")

    return value


def deserialize_tuple_from_list(
    value: Any,
    value_type: Type,
    recur: Recur,
) -> Any:
    if not isinstance(value, list):
        raise SerdeError(f"Expected list, got {value}")

    subtypes = typing.get_args(value_type)

    if len(value) != len(subtypes):
        raise SerdeError(
            f"Expected list of size {len(subtypes)}, but received one of size {len(value)}"
        )

    return tuple(recur(v, subtype) for v, subtype in zip(value, subtypes))


def deserialize_set_from_list(
    value: Any,
    value_type: Type,
    recur: Recur,
) -> Any:
    if not isinstance(value, list):
        raise SerdeError(f"Expected list, got {value}")

    subtype = typing.get_args(value_type)[0]

    return set(recur(v, subtype) for v in value)


def deserialize_class(
    value: Any,
    value_type: Type,
    recur: Recur,
) -> Any:
    assert inspect.isclass(value_type), value_type

    # Case: The class has a custom deserialization method
    try:
        override_method = getattr(value_type, "from_json")
    except AttributeError:
        pass
    else:
        if override_method.__func__ is not serde_class.Serde.from_json.__func__:
            return override_method(value)

    # Case: Enum
    if issubclass(value_type, Enum):
        if not isinstance(value, str):
            raise SerdeError(f"Expected enumeration string, got {value}")

        try:
            py_name = camel_case_to_all_upper(value)  # ValueError if not camel case
            return value_type[py_name]  # ValueError if not in enum
        except KeyError:
            raise SerdeError(f"Invalid enumeration value {value}") from None

    # Should this class be deserialized as a child? If so, find the actual
    # matching child class.
    if should_serialize_as_child(value_type):
        try:
            type_tag = value.pop("type")
        except KeyError:
            raise SerdeError(f'Object is missing the "type" field') from None

        candidate_classes = all_subclasses(value_type, True)

        for actual_type in candidate_classes:
            if upper_camel_case_to_camel_case(actual_type.__name__) == type_tag:
                break
        else:
            raise SerdeError(f'Object has an invalid type tag "{type_tag}"') from None

    else:
        actual_type = value_type

    del value_type

    # Case: Anything else
    if not isinstance(value, dict):
        raise SerdeError(f"Expected Object, got {value}")

    # Deserialize each field
    result = object.__new__(actual_type)  # type: ignore
    for field_name, field_type in typing.get_type_hints(actual_type).items():
        doc_name = all_lower_to_camel_case(field_name)

        try:
            field_value = recur(value.pop(doc_name), field_type)
        except KeyError:
            raise SerdeError(f'Object is missing the "{doc_name}" field') from None

        result.__dict__[field_name] = field_value  # type: ignore

    # Check for any superfluous fields
    if len(value) > 0:
        raise SerdeError(
            f"Superfluous object fields {', '.join(map(str, value.keys()))}"
        )

    return result


JSON_DESERIALIZERS: Dict[Type, Deserializer] = {
    bool: deserialize_bool_from_bool,
    int: deserialize_int_from_int,
    float: deserialize_float_from_float,
    bytes: deserialize_bytes_from_str,
    str: deserialize_str_from_str,
    datetime: deserialize_datetime_from_str,
    list: deserialize_list_from_list,
    dict: deserialize_dict_from_dict,
    Union: deserialize_optional,
    Any: deserialize_any,
    ObjectId: deserialize_object_id_from_str,
    Literal: deserialize_literal_as_is,
    tuple: deserialize_tuple_from_list,
    set: deserialize_set_from_list,
}


def from_json(
    value: Any,
    as_type: Type,
    *,
    custom_deserializers: Dict[Type, Callable[[Any], Any]] = {},
) -> Any:
    return common_deserialize(
        value,
        as_type,
        deserialize_class,
        JSON_DESERIALIZERS,
        custom_deserializers,
    )
