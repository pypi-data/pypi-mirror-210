import re
from enum import Enum, auto
from numbers import Number
from typing import Dict, List, Optional, Union, get_args

import casadi
import numpy as np
from pint import Unit

from optool.logging import LOGGER
from optool.uom import UNITS, Quantity
from optool.util import StrEnum

NUMERIC_TYPES = Union[Number, np.ndarray, Quantity]  # type:ignore #: Numbers with or without units of measurement
SYMBOLIC_TYPES = Union[casadi.SX]  #: Symbols used by the supported modeling languages


class VectorRepresentation(Enum):
    COLUMN = 0  #: Convenient shortcut to describe column vectors, where the entries are stacked vertically
    ROW = 1  #: Convenient shortcut to describe row vectors, where the entries are stacked horizontally


class Direction(StrEnum):
    ASCENDING = auto()
    DESCENDING = auto()


def has_offset(value_or_unit: Union[NUMERIC_TYPES, Unit]) -> bool:
    if isinstance(value_or_unit, Unit):
        return has_offset(Quantity(1.0, value_or_unit))
    # noinspection PyProtectedMember
    return isinstance(value_or_unit, Quantity) and not value_or_unit._is_multiplicative


def _get_unit(quantity_or_unit: Union[Quantity, Unit, str]) -> Unit:
    if isinstance(quantity_or_unit, Unit):
        return quantity_or_unit
    if isinstance(quantity_or_unit, str):
        return UNITS.parse_units(quantity_or_unit)
    if isinstance(quantity_or_unit, Quantity):
        return quantity_or_unit.units
    raise ValueError(
        f"The input argument must either be a quantity or a unit, but is {quantity_or_unit.__class__.__name__}")


def is_dimensionless(value_or_unit: Union[NUMERIC_TYPES, Unit, str]) -> bool:
    if isinstance(value_or_unit, (Quantity, Unit, str)):
        return _get_unit(value_or_unit).dimensionless
    return True


def is_compatible(value_or_unit: Union[NUMERIC_TYPES, Unit, str], unit: Optional[Union[Unit, str]]) -> bool:
    if unit is None:
        return is_dimensionless(value_or_unit)
    if isinstance(unit, str):
        unit = UNITS.parse_units(unit)
    both_are_dimensionless = is_dimensionless(value_or_unit) and is_dimensionless(unit)
    units_are_compatible = isinstance(value_or_unit,
                                      (Quantity, Unit, str)) and _get_unit(value_or_unit).is_compatible_with(unit)
    return both_are_dimensionless or units_are_compatible


def isnonnan(value: NUMERIC_TYPES):
    return ~np.isnan(value)  # type: ignore


def iszero(value: NUMERIC_TYPES):
    return value == 0


def isnonzero(value: NUMERIC_TYPES):
    return value != 0


def isnumeric(value) -> bool:
    return isinstance(value, get_args(NUMERIC_TYPES))


def is_symbolic(value) -> bool:
    return isinstance(value, SYMBOLIC_TYPES) or (  # type: ignore
        isinstance(value, Quantity) and is_symbolic(value.magnitude))  # type: ignore


def isscalar(value: Union[NUMERIC_TYPES, SYMBOLIC_TYPES]) -> bool:
    return num_elements(value) == 1


def isarray(value: NUMERIC_TYPES) -> bool:
    if isinstance(value, Number):
        return True
    if isinstance(value, np.ndarray):
        return np.ndim(value) == 1
    if isinstance(value, Quantity):
        return isarray(value.magnitude)
    raise TypeError(f"Unsupported type {type(value)}")


def isvector(value: Union[NUMERIC_TYPES, SYMBOLIC_TYPES],
             representation: Optional[VectorRepresentation] = None) -> bool:
    """
    Return True if value is a (column or row) vector, and False otherwise.

    Args:
        value (Union[NUMERIC_TYPES, OPT_VARIABLE_TYPES]): The value to check
        representation (VectorRepresentation): The representation of the vector

    Returns:
        True if value has two dimensions and is either a row or a column vector, depending on the requested axis

    See Also:
        :py:meth:`iscolumn`, :py:meth:`isrow`, :py:class:`VectorRepresentation`
    """
    if not representation:
        return iscolumn(value) or isrow(value)
    return iscolumn(value) if representation is VectorRepresentation.COLUMN else isrow(value)


def iscolumn(value: Union[NUMERIC_TYPES, SYMBOLIC_TYPES]) -> bool:
    if isinstance(value, Number):
        return True
    if isinstance(value, np.ndarray):
        return isscalar(value) or (value.ndim > 1 and value.shape[1] == 1)
    if isinstance(value, casadi.SX):
        return value.is_column()
    if isinstance(value, Quantity):
        return iscolumn(value.magnitude)
    raise TypeError(f"Unsupported type {type(value)}")


def isrow(value: Union[NUMERIC_TYPES, SYMBOLIC_TYPES]) -> bool:
    if isinstance(value, Number):
        return True
    if isinstance(value, np.ndarray):
        return isscalar(value) or (value.ndim > 1 and value.shape[0] == 1)
    if isinstance(value, casadi.SX):
        return value.is_row()
    if isinstance(value, Quantity):
        return isrow(value.magnitude)
    raise TypeError(f"Unsupported type {type(value)}")


def num_elements(value: Union[NUMERIC_TYPES, SYMBOLIC_TYPES]) -> int:
    if isinstance(value, Quantity):
        return num_elements(value.magnitude)
    if isnumeric(value):
        return np.size(value)  # type: ignore
    if isinstance(value, casadi.SX):
        return value.numel()
    raise TypeError(f"Unsupported type {type(value)}")


def is_monotonic(value: NUMERIC_TYPES, direction: Direction = Direction.ASCENDING, strict: bool = False) -> bool:
    if num_elements(value) < 2:
        raise ValueError(f"Requires at least 2 elements, but got only {num_elements(value)}.")
    if not all(isnonnan(value)):
        raise ValueError(f"The array contains {np.sum(~isnonnan(value))} NaN value(s).")

    difference = np.diff(value)  # type: ignore
    if direction is Direction.ASCENDING:
        if strict:
            return bool(np.all(difference > 0))
        return bool(np.all(difference >= 0))
    if strict:
        return bool(np.all(difference < 0))
    return bool(np.all(difference <= 0))


_REFERENCES: Dict[str, Quantity] = {}


def is_value_satisfying(quantity: Quantity, criterion: str) -> bool:
    stripped = criterion.replace(" ", "")
    try:
        relation = re.match(r"^(<=|==|!=|>=|<|≤|=|≠|≥|>)", stripped).group()  # type: ignore
        reference_string = stripped.lstrip(relation)
    except AttributeError as e:
        raise ValueError(f"The given criterion {criterion!r} does not start with any of the following "
                         f"relational symbols: <|≤|<=|=|==|!=|≠|≥|>=|>") from e

    if reference_string in _REFERENCES:
        reference = _REFERENCES[reference_string]
    else:
        try:
            reference = Quantity(reference_string)
            _REFERENCES[reference_string] = reference
        except Exception as e:
            raise ValueError(f"Cannot create a quantity from {reference_string!r}.") from e

    if not is_compatible(quantity, reference.units):
        raise ValueError(f"Cannot compare quantity with units {quantity.units!r} to {reference.units!r}.")

    LOGGER.debug("From {}, we interpret the following: Is {} {} {} true?", criterion, quantity, relation, reference)
    if relation == "<":
        return bool(np.all(quantity < reference))
    elif relation in ["≤", "<="]:
        return bool(np.all(quantity <= reference))
    elif relation in ["=", "=="]:
        return bool(np.all(quantity == reference))
    elif relation in ["!=", "≠"]:
        return bool(np.all(quantity != reference))
    elif relation in ["≥", ">="]:
        return bool(np.all(quantity >= reference))
    elif relation == ">":
        return bool(np.all(quantity > reference))
    else:
        raise ValueError(f"Unsupported relational symbol {relation!r}.")


def consecutive(data: np.ndarray, step_size: int = 1) -> List[np.ndarray]:
    return np.split(data, np.where(np.diff(data) != step_size)[0] + 1)
