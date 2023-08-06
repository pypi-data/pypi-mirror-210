from __future__ import annotations

from typing import Any, Dict

from pint import Unit
from pint.util import to_units_container
from pint_pandas import PintArray

from optool.serialization import AllowedSerializedDictKeys, Serializer
from optool.uom import UNITS, Quantity


class PintQuantitySerializer(Serializer[Quantity]):

    def serialize(self, obj: Quantity) -> Dict[AllowedSerializedDictKeys, Any]:
        return {'mag': obj.m, 'unit': obj.u}

    def deserialize(self, raw: Dict[AllowedSerializedDictKeys, Any]) -> Quantity:
        return Quantity(raw['mag'], raw['unit'])


class PintUnitSerializer(Serializer[Unit]):

    def serialize(self, obj: Unit) -> Dict[AllowedSerializedDictKeys, Any]:
        return dict(to_units_container(obj))

    def deserialize(self, raw: Dict[AllowedSerializedDictKeys, Any]) -> Unit:
        return UNITS.Unit(UNITS.UnitsContainer(raw))


class PintArraySerializer(Serializer[PintArray]):

    def serialize(self, obj: PintArray) -> Dict[AllowedSerializedDictKeys, Any]:
        return {'mag': obj.quantity.m, 'unit': obj.quantity.u}

    def deserialize(self, raw: Dict[AllowedSerializedDictKeys, Any]) -> PintArray:
        return PintArray(raw['mag'], raw['unit'])
