import math
from abc import ABC
from typing import Any, Dict, Optional, Union, final

import numpy as np
from pint import Unit
from pydantic import Field, StrictStr, root_validator, validator

from optool import BaseModel
from optool.fields.misc import PositiveFiniteFloat
from optool.fields.numeric import ImmutableArray
from optool.fields.quantities import QuantityLike
from optool.fields.symbolic import CasadiColumn
from optool.math import num_elements
from optool.uom import Quantity


class OptimizationConstraint(BaseModel, ABC):
    """
    Constraint for an NLP formulation.

    This handle class allows to define a set of constraints which is then used for an NLP formulation.

    The set of constraints may be scalar or a vector.
    """

    name: StrictStr = ""
    """
    The name of the constraint.
    """

    nominal_value: Optional[PositiveFiniteFloat] = Field(None, allow_mutation=False)
    """
    The nominal value for scaling the constraint.
    """

    lagrange_multipliers: Optional[QuantityLike[Any, ImmutableArray]] = None
    """
    The lagrange multipliers obtained after solving the NLP.
    """


class ExpressionConstraint(OptimizationConstraint):
    """
    Directly creates a constraint object from a symbolic expression.
    """

    expression: QuantityLike[Any, Union[ImmutableArray, CasadiColumn]] = Field(allow_mutation=False)
    """
    The expression of the constraint.
    """


class BoxConstraint(OptimizationConstraint):
    """
    Creates a box constraint.
    """

    expression: QuantityLike[Any, CasadiColumn] = Field(allow_mutation=False,
                                                        exclude=True)  # Cannot handle casadi elements
    """
    The expression of the constraint.
    """

    lower_bound: Optional[QuantityLike[Any, ImmutableArray]] = Field(allow_mutation=False)
    """
    The smallest values the expression should be able to take.
    """

    upper_bound: Optional[QuantityLike[Any, ImmutableArray]] = Field(allow_mutation=False)
    """
    The greatest values the expression should be able to take.
    """

    @final
    @validator('lower_bound', 'upper_bound')
    def _inflate_scalar_if_necessary(cls, value: Quantity, values: Dict) -> Quantity:
        if value is None:
            return value

        expression_length = values['expression'].magnitude.numel()
        if np.size(value.magnitude) == 1 and expression_length > 1:
            return Quantity(np.full(expression_length, value.magnitude), value.units)

        return value

    @final
    @root_validator
    def _is_consistent(cls, values: Dict) -> Dict:
        numerical_values = [key for (key, value) in values.items() if isinstance(value, Quantity)]
        array_lengths: Dict[str, int] = {key: num_elements(values[key].magnitude) for key in numerical_values}
        unique_lengths = np.unique(list(array_lengths.values()))

        if np.size(unique_lengths) != 1:
            raise ValueError(f"Not all arrays have the same number of elements, see {array_lengths}")

        same_unit_values = ('expression', 'lower_bound', 'upper_bound')
        array_units: Dict[str, Unit] = {key: values[key].units for key in same_unit_values if values[key] is not None}
        other_units = array_units.copy()
        reference_unit = other_units.popitem()[1]  # removes one item

        if any(not reference_unit.is_compatible_with(other) for other in list(other_units.values())):
            raise ValueError(f"Not all numerical values have compatible units, see {array_units}")

        return values

    def get_symbols(self) -> CasadiColumn:
        return self.expression.magnitude

    def get_dimensionless_lower_bound(self) -> np.ndarray:
        if self.lower_bound is None:
            return np.full((self.length(),), -math.inf)
        return self.lower_bound.m_as(self.get_unit())

    def get_dimensionless_upper_bound(self) -> np.ndarray:
        if self.upper_bound is None:
            return np.full((self.length(),), math.inf)
        return self.upper_bound.m_as(self.get_unit())

    def get_unit(self) -> Unit:
        return self.expression.units

    def length(self) -> int:
        return self.get_symbols().numel()
