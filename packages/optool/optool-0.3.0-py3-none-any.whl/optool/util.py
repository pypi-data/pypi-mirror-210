from __future__ import annotations

from enum import Enum

import numpy as np

from optool import BaseModel
from optool.fields.misc import NonEmptyStr


class StrEnum(str, Enum):

    def _generate_next_value_(self, *_):
        return self.lower()


class ValueRange(BaseModel, frozen=True):
    """
    Ranges of the normed values of the optimization variables.
    """

    name: NonEmptyStr
    """
    The name of the decision variable.
    """

    min: float
    avg: float
    max: float
    max_abs: float

    @classmethod
    def of(cls, name: str, val: np.ndarray):
        """

        Args:
            name: The name of the decision variable.
            val: The normed values as array.
        """
        return cls(name=name, min=np.min(val), avg=float(np.mean(val)), max=np.max(val), max_abs=np.max(np.abs(val)))
