from __future__ import annotations

from numbers import Number
from typing import TYPE_CHECKING, Any, Generic, TypeVar

from pint import Unit
from pydantic import ValidationError
from pydantic.fields import ModelField

from optool.fields.util import WrongTypeError, check_validation_is_passed_on_to_sub_types, get_type_validator
from optool.uom import UNITS, PhysicalDimension, Quantity


class DimensionalityError(ValueError):

    def __init__(self, *, expected: str, value: Quantity) -> None:
        super().__init__(f"expected the dimensionality {expected}, "
                         f"but got a value with dimensionality {value.dimensionality}")


class UnsupportedMagnitudeConversion(ValueError):

    def __init__(self, *, value: Any) -> None:
        super().__init__(f"the value of {type(value)} cannot be converted automatically")


class UnitParseError(ValueError):

    def __init__(self, *, unit: str) -> None:
        super().__init__(f"cannot parse the unit {unit}")


D = TypeVar("D", bound=PhysicalDimension)


class ConstrainedUnit(Unit, Generic[D]):
    """
    Pydantic-compatible field type for :py:class:`pint.Unit` objects, which allows to specify the desired
    dimensionality.

    See Also:
        `Pydantic documentation: Custom Data Types <https://docs.pydantic.dev/usage/types/#custom-data-types>`_ and
        class :py:class:`pydantic.types.ConstrainedInt` or similar of :py:mod:`pydantic`
    """
    strict: bool = True

    @classmethod
    def __get_validators__(cls):
        yield get_type_validator(Unit) if cls.strict else cls.validate_unit
        yield cls.validate_dimensionality

    @classmethod
    def validate_unit(cls, value: Any, field: ModelField) -> Unit:
        if isinstance(value, Unit):
            return value

        if isinstance(value, str):
            try:
                return UNITS.parse_units(value)
            except Exception as e:
                raise UnitParseError(unit=value) from e

        raise WrongTypeError(expected=(Unit, str), value=value)

    @classmethod
    def validate_dimensionality(cls, val: Unit, field: ModelField) -> Unit:
        if not field.sub_fields or field.sub_fields[0].type_ == Any:
            return val

        dimension = field.sub_fields[0].type_
        if not issubclass(dimension, PhysicalDimension):
            raise TypeError(f"Unsupported {dimension}, should be a {PhysicalDimension.__name__!r} or 'typing.Any'.")
        elif val.dimensionality != UNITS.get_dimensionality(dimension.dimensionality):
            raise DimensionalityError(expected=dimension.dimensionality, value=val)
        return val


T = TypeVar("T")  # Allow storing anything as magnitude in Quantity


class ConstrainedQuantity(Quantity, Generic[D, T]):
    """
    Pydantic-compatible field type for :py:class:`pint.Quantity` objects, which allows to specify the desired
    dimensionality.

    See Also:
        Class :py:class:`pydantic.types.ConstrainedInt` or similar of :py:mod:`pydantic`.
    """

    strict: bool = True
    strict_subtypes: bool = True

    @classmethod
    def __get_validators__(cls):
        subtype_provider = (lambda x: type(x.m)) if cls.strict_subtypes else None
        yield get_type_validator(Quantity, subtype_provider) if cls.strict else cls.validate_quantity
        yield cls.validate_dimensionality
        yield cls.validate_magnitude

    @classmethod
    def validate_quantity(cls, val: Any, field: ModelField) -> Quantity:
        try:
            return Quantity(val)
        except Exception as e:
            raise WrongTypeError(expected=(Quantity, str, Number), value=val) from e

    @classmethod
    def validate_dimensionality(cls, val: Quantity, field: ModelField) -> Quantity:
        if not field.sub_fields or field.sub_fields[0].type_ == Any:
            return val

        dimension = field.sub_fields[0].type_
        if not issubclass(dimension, PhysicalDimension):
            raise TypeError(f"Unsupported {dimension}, should be a {PhysicalDimension.__name__!r} or 'typing.Any'.")
        elif not val.check(dimension.dimensionality):
            raise DimensionalityError(expected=dimension.dimensionality, value=val)
        return val

    @classmethod
    def validate_magnitude(cls, val: Quantity, field: ModelField) -> Quantity:
        if not field.sub_fields:
            return val

        magnitude_field = field.sub_fields[1]
        check_validation_is_passed_on_to_sub_types(field.name, magnitude_field)
        valid_value, error = magnitude_field.validate(val.m, {}, loc='magnitude')
        if error:
            raise ValidationError([error], cls)

        return Quantity(valid_value, val.u)


if TYPE_CHECKING:
    UnitLike = Unit
    StrictUnit = Unit

    QuantityLike = Quantity
    StrictQuantity = Quantity

else:

    class UnitLike(ConstrainedUnit[D]):
        strict = False

    class StrictUnit(ConstrainedUnit[D]):
        strict = True

    class QuantityLike(ConstrainedQuantity[D, T]):
        strict = False
        strict_subtypes = False

    class StrictQuantity(ConstrainedQuantity[D, T]):
        strict = True
        strict_subtypes = False
