from __future__ import annotations

from typing import Any, Dict

import numpy as np

from optool.serialization import AllowedSerializedDictKeys, Serializer


class NumpyNdArraySerializer(Serializer[np.ndarray]):

    def serialize(self, obj: np.ndarray) -> Dict[AllowedSerializedDictKeys, Any]:
        return {"datatype": obj.dtype.name, "writeable": obj.flags.writeable, "values": obj.tolist()}

    def deserialize(self, raw: Dict[AllowedSerializedDictKeys, Any]) -> np.ndarray:
        value = np.asarray(raw["values"], dtype=raw["datatype"])
        value.setflags(write=raw['writeable'])
        return value
