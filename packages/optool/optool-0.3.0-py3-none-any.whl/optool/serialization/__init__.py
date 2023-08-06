from __future__ import annotations

import json
from abc import ABC, abstractmethod
from collections import OrderedDict
from typing import Any, Callable, Dict, ForwardRef, Generic, Type, TypeVar, Union, get_args

from optool.logging import LOGGER

T = TypeVar("T")
AllowedSerializedDictKeys = Union[str, int, float, bool, None]


class Serializer(ABC, Generic[T]):
    _type_T: type

    def __init_subclass__(cls) -> None:
        # Get the generic type. Approach taken from https://stackoverflow.com/a/71720366
        # noinspection PyUnresolvedReferences
        cls._type_T = get_args(cls.__orig_bases__[0])[0]  # type: ignore

    @classmethod
    def get_type(cls) -> type:
        return cls._type_T

    @classmethod
    def get_type_name(cls) -> str:
        return str(cls.get_type())

    @abstractmethod
    def serialize(self, obj: T) -> Dict[AllowedSerializedDictKeys, Any]:
        """
        Serializes an object to a dictionary of primitive types.
        """
        raise NotImplementedError()

    @abstractmethod
    def deserialize(self, raw: Dict[AllowedSerializedDictKeys, Any]) -> T:
        """
        Deserializes a dictionary of primitive types to an object.
        """
        raise NotImplementedError()


class SerializationAssistant:
    _serializers: Dict[str, Serializer] = {}

    @classmethod
    def register(cls, *serializers: Serializer) -> Dict[Union[Type[Any], str, ForwardRef], Callable]:
        for serializer in serializers:
            obj_type = serializer.get_type()
            obj_type_name = serializer.get_type_name()
            LOGGER.debug("Registering serializer for {}.", obj_type)
            if obj_type_name in cls._serializers:
                raise ValueError(f"There is already an entry in the registry for {obj_type_name}.")
            cls._serializers[obj_type_name] = serializer

        return {serializer.get_type(): cls._create_json_encoder(serializer) for serializer in serializers}

    @staticmethod
    def _create_json_encoder(serializer: Serializer[T]) -> Callable[[T], Dict[AllowedSerializedDictKeys, Any]]:

        def _encode_obj(obj: T) -> Dict[AllowedSerializedDictKeys, Any]:
            return OrderedDict({'obj_type': serializer.get_type_name()}, **serializer.serialize(obj))

        return _encode_obj

    @classmethod
    def json_loader(cls, raw: Union[str, bytes]) -> Any:
        return json.loads(raw, object_pairs_hook=cls._parse_raw)

    @classmethod
    def _parse_raw(cls, tuples: list[tuple[Any, Any]]) -> Any:
        dct = OrderedDict(tuples)

        if 'obj_type' not in dct:
            return dct

        obj_type = dct.pop('obj_type')
        if obj_type not in cls._serializers:
            raise ValueError(f"The registry has no entry for {obj_type}. Have only {cls._serializers.keys()}.")
        return cls._serializers[obj_type].deserialize(dct)
