from __future__ import annotations

import itertools
from typing import TYPE_CHECKING, Optional

import casadi
import numpy as np

from optool.fields.util import get_type_validator


class ShapeError(ValueError):

    def __init__(self, *, expected: tuple[int, ...], value: casadi.SX) -> None:
        super().__init__(f"expected the shape {expected}, "
                         f"but got a value with shape ('called size' in CasADi) {value.size()}")


class ConstrainedCasadiSymbol:
    """
    Pydantic-compatible field type for :py:class:`casadi.SX` objects.

    See Also:
        `Pydantic documentation: Custom Data Types <https://docs.pydantic.dev/usage/types/#custom-data-types>`_ and
        class :py:class:`pydantic.types.ConstrainedInt` or similar of :py:mod:`pydantic`
    """

    shape: Optional[tuple[int, ...]] = None

    @classmethod
    def __get_validators__(cls):
        yield get_type_validator(casadi.SX)
        yield cls.validate_shape

    @classmethod
    def validate_shape(cls, val: casadi.SX) -> np.ndarray:
        if cls.shape is None or all(cls._compare_dim(*dims) for dims in itertools.zip_longest(cls.shape, val.size())):
            return val
        raise ShapeError(expected=cls.shape, value=val)

    @classmethod
    def _compare_dim(cls, expected: Optional[int], actual: Optional[int]) -> bool:
        return actual == expected or expected == -1


if TYPE_CHECKING:

    CasadiScalar = CasadiRow = CasadiColumn = CasadiMatrix = casadi.SX

else:

    class CasadiScalar(ConstrainedCasadiSymbol):
        """
        Pydantic-compatible field type for two-dimensional :py:class:`casadi.SX` objects representing scalars.
        """
        shape = (1, 1)

    class CasadiRow(ConstrainedCasadiSymbol):
        """
        Pydantic-compatible field type for two-dimensional :py:class:`casadi.SX` objects representing row vectors.
        """
        shape = (1, -1)

    class CasadiColumn(ConstrainedCasadiSymbol):
        """
        Pydantic-compatible field type for two-dimensional :py:class:`casadi.SX` objects representing column vectors.
        """
        shape = (-1, 1)

    class CasadiMatrix(ConstrainedCasadiSymbol):
        """
        Pydantic-compatible field type for two-dimensional :py:class:`casadi.SX` objects representing matrices.
        """
        shape = (-1, -1)
