import math
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Union, final

import casadi
import numpy as np
from pint import Unit
from pydantic import StrictBool, root_validator, validator

from optool import BaseModel
from optool.fields.misc import NonEmptyStr
from optool.fields.numeric import ImmutableArray
from optool.fields.quantities import QuantityLike
from optool.fields.util import validate
from optool.logging import LOGGER
from optool.math import SYMBOLIC_TYPES, has_offset, num_elements
from optool.uom import UNITS, Quantity


class OptimizationVariable(BaseModel, ABC):
    """
    Set of decision variables for an NLP formulation.

    This handle class allows to define a set of decision variables which is then used for an NLP formulation.

    The set of decision variables may be scalar or a vector.
    """

    _frozen_nominal_values: StrictBool = False
    """Indicator flag to ensure that nominal values cannot be changed anymore. Shouldn't be set manually."""

    name: NonEmptyStr
    """The name of the decision variable."""

    unit: Unit = None
    """The physical unit_of_scaling_variable of the decision variable."""

    initial_guess: QuantityLike[Any, ImmutableArray]
    """The initial values to provide to the solver."""

    lower_bounds: QuantityLike[Any, ImmutableArray]
    """The minimum values allowed for the decision variable."""

    upper_bounds: QuantityLike[Any, ImmutableArray]
    """The maximum values allowed for the decision variable."""

    nominal_values: QuantityLike[Any, ImmutableArray]
    """The nominal values for scaling the variables."""

    solution: Optional[QuantityLike[Any, ImmutableArray]] = None
    """The solution obtained after solving the NLP."""

    lagrange_multipliers: Optional[QuantityLike[Any, ImmutableArray]] = None
    """The lagrange multipliers obtained after solving the NLP."""

    @final
    @validator('unit', allow_reuse=True)
    def _is_offset_free(cls, value):
        return validate(value, lambda x: not has_offset(x), 'The unit should be offset-free, but {value} is not.')

    @final
    @validator('initial_guess', 'lower_bounds', 'upper_bounds', 'nominal_values', allow_reuse=True)
    def _inflate_scalar_if_necessary(cls, value: Quantity, values: Dict):
        if np.size(value.magnitude) == 1:
            array_lengths, numerical_values, unique_lengths = cls._get_array_lengths(values)

            if np.size(unique_lengths) == 1 and unique_lengths > 1:
                return Quantity(np.full(unique_lengths, value.magnitude), value.units)

        return value

    @validator('initial_guess', 'nominal_values', allow_reuse=True)
    def _is_finite(cls, value):
        return validate(value, lambda x: np.all(np.isfinite(x)), 'All array elements must be finite, but have {value}.')

    @final
    @validator('lower_bounds', 'upper_bounds', allow_reuse=True)
    def _is_not_nan(cls, value):
        return validate(value, lambda x: np.all(~np.isnan(x)), 'At least one array elements is NaN, see {value}.')

    @final
    @validator('nominal_values', allow_reuse=True)
    def _is_not_zero(cls, value):
        return validate(value, lambda x: np.all(x != 0), 'At least one array elements is zero, see {value}.')

    @final
    @validator('nominal_values', allow_reuse=True)
    def _is_not_frozen(cls, value, values: Dict):
        flag_field_name = '_frozen_nominal_values'
        frozen = values.get(flag_field_name, cls.__private_attributes__[flag_field_name].default)
        return validate(value, not frozen, 'Cannot change nominal value after retrieving the regular variable.')

    @final
    @root_validator(allow_reuse=True)
    def _is_consistent(cls, values: Dict) -> Dict:
        array_lengths, numerical_values, unique_lengths = cls._get_array_lengths(values)

        if np.size(unique_lengths) != 1:
            raise ValueError(f"Not all arrays have the same number of elements, see {array_lengths}")

        unit = values['unit'] or UNITS.dimensionless
        array_units: Dict[str, Unit] = {key: values[key].units for key in numerical_values}

        if any(not unit.is_compatible_with(other) for other in list(array_units.values())):
            raise ValueError(f"Not all numerical values have compatible units, see {array_units}")

        return values

    @staticmethod
    def _get_array_lengths(values: Dict):
        numerical_values = [key for (key, value) in values.items() if isinstance(value, Quantity)]
        array_lengths: Dict[str, int] = {key: num_elements(values[key].magnitude) for key in numerical_values}
        unique_lengths = np.unique(list(array_lengths.values()))
        return array_lengths, numerical_values, unique_lengths

    @abstractmethod
    def length(self) -> int:
        """
        Gets the number of symbols.
        """
        raise NotImplementedError()

    @property
    @abstractmethod
    def normed(self) -> SYMBOLIC_TYPES:
        raise NotImplementedError()

    @property
    @abstractmethod
    def regular(self) -> Quantity:
        raise NotImplementedError()

    def _freeze_nominal_values(self):
        if not self._frozen_nominal_values:
            LOGGER.debug("Freezing nominal values of variable named {}.", self.name)
            self._frozen_nominal_values = True

    @staticmethod
    def casadi(name: str, n: int, unit: Optional[Unit] = None):
        return CasadiVariable(name, n, unit)


class CasadiVariable(OptimizationVariable):
    """
    Representation of a decision variable using the modeling language CasADi.
    """

    _symbols: casadi.SX

    def __init__(self, name: str, n: int, unit: Optional[Unit] = None):
        super().__init__(name=name,
                         unit=unit,
                         initial_guess=Quantity(np.zeros((n,)), unit),
                         lower_bounds=Quantity(np.full((n,), -math.inf), unit),
                         upper_bounds=Quantity(np.full((n,), math.inf), unit),
                         nominal_values=Quantity(np.ones((n,)), unit))
        self._symbols = casadi.SX.sym(self.name, n, 1)

    @final
    @root_validator
    def _is_consistent_with_symbol_size(cls, values: Dict) -> Dict:
        numerical_values = [key for (key, value) in values.items() if isinstance(value, Quantity)]
        array_lengths: Dict[str, int] = {key: np.size(values[key].magnitude) for key in numerical_values}

        if '_symbols' not in values:  # cannot validate yet (class is still being initialized)
            return values

        symbol_size = values['_symbols'].numel()
        if any(symbol_size != size for size in array_lengths.values()):
            raise ValueError(f"Not all numerical values have the same number of elements than the number of symbols "
                             f"({symbol_size}), see {array_lengths}")

        return values

    @property
    def normed(self) -> casadi.SX:
        return self._symbols

    @property
    def regular(self) -> Union[casadi.SX, Quantity]:
        self._freeze_nominal_values()
        return self._symbols * self.nominal_values

    def length(self) -> int:
        return self._symbols.numel()
