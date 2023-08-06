from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple, Union

from bson import ObjectId

from . import serde_class, serde_json
from .common import *

__all__ = [
    "as_bson",
    "from_bson",
    "Bsonable",
]


Bsonable = Union[
    None,
    bool,
    int,
    float,
    str,
    Dict[str, "Bsonable"],
    List["Bsonable"],
    Tuple["Bsonable", ...],
    bytes,
    ObjectId,
    datetime,
]


def serialize_bytes_to_bytes(
    value: Any,
    value_type: Type,
    recur: Recur,
) -> bytes:
    assert isinstance(value, bytes), value
    return value


def serialize_datetime_to_datetime(
    value: Any,
    value_type: Type,
    recur: Recur,
) -> datetime:
    assert isinstance(value, datetime), value
    assert (
        value.tzinfo is not None
    ), f"Encountered datetime without a timezone. Please always set timezones, or expect hard to find bugs."

    return value


def serialize_object_id_to_object_id(
    value: Any,
    value_type: Type,
    recur: Recur,
) -> ObjectId:
    assert isinstance(value, ObjectId), value
    return value


def serialize_class(
    value: Any,
    value_type: Type,
    recur: Recur,
) -> Dict[str, Any]:
    result = serde_json.serialize_class(value, value_type, recur)

    # Case: The class has a custom serialization method
    try:
        override_method = getattr(value, "as_bson")
    except AttributeError:
        pass
    else:
        if override_method.__func__ is not serde_class.Serde.as_bson:
            return override_method()

    # Map "id" to "_id", as is done in MongoDB.
    if isinstance(result, dict) and "_id" not in result:
        try:
            result["_id"] = result.pop("id")
        except KeyError:
            pass

    return result


BSON_SERIALIZERS: Dict[Type, Serializer] = serde_json.JSON_SERIALIZERS.copy()
BSON_SERIALIZERS.update(
    {
        bytes: serialize_bytes_to_bytes,
        datetime: serialize_datetime_to_datetime,
        ObjectId: serialize_object_id_to_object_id,
    }
)


def as_bson(
    value: Any,
    *,
    as_type: Optional[Type] = None,
    custom_serializers: Dict[Type, Callable[[Any], Any]] = {},
) -> Bsonable:
    return common_serialize(
        value,
        type(value) if as_type is None else as_type,
        serialize_class,
        BSON_SERIALIZERS,
        custom_serializers,
    )


def deserialize_bytes_from_bytes(
    value: Any,
    value_type: Type,
    recur: Recur,
) -> bytes:
    if not isinstance(value, bytes):
        raise SerdeError(f"Expected bytes, got {value}")

    return value


def deserialize_datetime_from_datetime(
    value: Any,
    value_type: Type,
    recur: Recur,
) -> datetime:
    if not isinstance(value, datetime):
        raise SerdeError(f"Expected datetime, got {value}")

    # BSON doesn't support timezones, and MongoDB convention dictates UTC to be
    # assumed. Impute that.
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)

    return value


def deserialize_object_id_from_object_id(
    value: Any,
    value_type: Type,
    recur: Recur,
) -> ObjectId:
    if not isinstance(value, ObjectId):
        raise SerdeError(f"Expected ObjectId, got {value}")

    return value


def deserialize_class(
    value: Any,
    value_type: Type,
    recur: Recur,
) -> Dict[str, Any]:
    # Case: The class has a custom deserialization method
    try:
        override_method = getattr(value_type, "from_bson")
    except AttributeError:
        pass
    else:
        if override_method.__func__ is not serde_class.Serde.from_bson.__func__:
            return override_method(value)

    # Map "_id" to "id"
    if isinstance(value, dict) and "id" not in value:
        try:
            value["id"] = value.pop("_id")
        except KeyError:
            pass

    # Then hand off to the JSON deserializer.
    return serde_json.deserialize_class(value, value_type, recur)


BSON_DESERIALIZERS: Dict[Type, Deserializer] = serde_json.JSON_DESERIALIZERS.copy()
BSON_DESERIALIZERS.update(
    {
        bytes: deserialize_bytes_from_bytes,
        datetime: deserialize_datetime_from_datetime,
        ObjectId: deserialize_object_id_from_object_id,
    }
)


def from_bson(
    value: Any,
    as_type: Type,
    *,
    custom_deserializers: Dict[Type, Callable[[Any], Any]] = {},
) -> Any:
    return common_deserialize(
        value,
        as_type,
        deserialize_class,
        BSON_DESERIALIZERS,
        custom_deserializers,
    )
