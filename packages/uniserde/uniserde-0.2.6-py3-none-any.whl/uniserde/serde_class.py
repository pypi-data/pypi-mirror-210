from typing import Any, Callable, Dict, Optional, Type, TypeVar

from . import schema_mongodb, serde_bson, serde_json

T = TypeVar("T", bound="Serde")


class Serde:
    def as_bson(
        self,
        *,
        as_type: Optional[Type] = None,
        custom_serializers: Dict[Type, Callable[[Any], Any]] = {},
    ) -> Dict[str, serde_bson.Bsonable]:
        """
        Serialize the entire instance to BSON, by applying the field serializer
        to each field. Field names are converted to camel case.
        """
        assert as_type is None or issubclass(self.__class__, as_type), as_type
        return serde_bson.as_bson(
            self,
            as_type=as_type,
            custom_serializers=custom_serializers,
        )  # type: ignore

    def as_json(
        self,
        *,
        as_type: Optional[Type] = None,
        custom_serializers: Dict[Type, Callable[[Any], Any]] = {},
    ) -> Dict[str, serde_json.Jsonable]:
        """
        Serialize the entire instance to JSON, by applying the field serializer
        to each field. Field names are converted to camel case.
        """
        assert as_type is None or issubclass(self.__class__, as_type), as_type
        return serde_json.as_json(
            self,
            as_type=as_type,
            custom_serializers=custom_serializers,
        )  # type: ignore

    @classmethod
    def from_bson(
        cls: Type[T],
        document: Dict[str, Any],
        custom_deserializers: Dict[Type, Callable[[Any], Any]] = {},
    ) -> T:
        """
        Deserialize an entire data class from BSON, by applying the field
        deserializer to each field. Field names are converted to camel case. The
        value may be modified by this function!
        """
        return serde_bson.from_bson(
            document,
            as_type=cls,
            custom_deserializers=custom_deserializers,
        )

    @classmethod
    def from_json(
        cls: Type[T],
        document: Dict[str, Any],
        custom_deserializers: Dict[Type, Callable[[Any], Any]] = {},
    ) -> T:
        """
        Deserialize an entire data class from JSON, by applying the field
        deserializer to each field. Field names are converted to camel case. The
        value may be modified by this function!
        """
        return serde_json.from_json(
            document,
            as_type=cls,
            custom_deserializers=custom_deserializers,
        )

    @classmethod
    def as_mongodb_schema(
        cls,
        custom_handlers: Dict[Type, Callable[[Any], Any]] = {},
    ) -> Any:
        return schema_mongodb.as_mongodb_schema(
            cls,
            custom_handlers=custom_handlers,
        )
