from __future__ import annotations

from numbers import Number
from typing import TYPE_CHECKING, Any, Generic, Iterable, Sequence, Type, TypeVar, cast

import numpy as np
import pandas as pd
from pandas import DatetimeIndex, Index, TimedeltaIndex
from pint_pandas import PintArray
from pydantic import ValidationError
from pydantic.fields import ModelField

from optool.fields.util import WrongTypeError, check_sub_fields_level, get_type_validator
from optool.uom import PhysicalDimension, Quantity


class IndexTypeError(ValueError):

    def __init__(self, *, expected: Type[Index], value: pd.Series) -> None:
        super().__init__(f"expected index type {expected}, but got a series with index type {type(value.index)}")


class DimensionalityError(ValueError):

    def __init__(self, *, expected: str, value: pd.Series) -> None:
        super().__init__(f"expected the dimensionality {expected}, but got a series with data-type {value.dtype}")


class ArrayWriteableError(ValueError):

    def __init__(self, *, expected: bool, value: np.ndarray) -> None:
        super().__init__(f"expected writeable is {expected}, "
                         f"but got a value with writeable flag set to {value.flags.writeable}")


T = TypeVar("T")  # Allow storing anything as data-type in Series


class ConstrainedSeries(pd.Series, Generic[T]):
    """
    Pydantic-compatible field type for :py:class:`pandas.Series` objects, which allows to specify the data-type.

    See Also:
        `Pydantic documentation: Custom Data Types <https://docs.pydantic.dev/usage/types/#custom-data-types>`_ and
        class :py:class:`pydantic.types.ConstrainedInt` or similar of :py:mod:`pydantic`
    """

    strict: bool = True
    index_type: Type[Index] = pd.RangeIndex

    @classmethod
    def __get_validators__(cls):
        yield get_type_validator(pd.Series) if cls.strict else cls.validate_series
        yield cls.validate_index_type
        yield cls.validate_dimensionality
        yield cls.validate_data_type
        # yield cls.validate_writeable

    @classmethod
    def validate_series(cls, val: Any, field: ModelField) -> pd.Series:
        if isinstance(val, pd.Series):
            return val
        if not field.sub_fields:
            return pd.Series(val)

        if isinstance(val, Sequence) and len(val) == 2 and isinstance(val[1], Index):
            index = val[1]
            val = val[0]
        else:
            index = None

        check_sub_fields_level(field)
        data_type = field.sub_fields[0].type_

        if cls._is_physical_dimension(field.sub_fields[0]):
            # Now, we assume the output should have units
            pre_parsed_scalar_types = (str, Number, np.ndarray, Iterable)
            if isinstance(val, pre_parsed_scalar_types):
                try:
                    val = Quantity(val)
                except Exception as e:
                    raise WrongTypeError(expected=pre_parsed_scalar_types, value=val) from e

            val = cls._make_iterable_quantity(val)
            try:
                pint_array = PintArray(val)
            except Exception as e:
                raise ValueError(f"Cannot create a {PintArray.__name__} from {val}.") from e
            try:
                return pd.Series(pint_array, index=index)
            except Exception as e:
                raise ValueError(f"Cannot create a {pd.Series.__name__} from {PintArray.__name__} due to {e!r}.") from e

        # Validate each element separately
        valid_value = []
        iterable = cls._make_iterable_quantity(val) if isinstance(val, Iterable) else [val]
        for (i, el) in enumerate(iterable):
            valid_element, error = field.sub_fields[0].validate(el, {}, loc=f'element_{i}')
            if error:
                raise ValidationError([error], cls)
            valid_value.append(valid_element)

        return pd.Series(valid_value, index=index, dtype=data_type)

    @classmethod
    def validate_index_type(cls, val: pd.Series, field: ModelField) -> pd.Series:
        if cls.index_type is None or isinstance(val.index, cls.index_type):
            return val
        raise IndexTypeError(expected=cls.index_type, value=val)

    @classmethod
    def validate_dimensionality(cls, val: pd.Series, field: ModelField) -> pd.Series:
        if not field.sub_fields or not cls._is_physical_dimension(field.sub_fields[0]):
            return val

        if not isinstance(val.array, PintArray):
            raise WrongTypeError(expected=PintArray, value=val.array)

        dimension = field.sub_fields[0].type_
        if dimension == Any or cast(PintArray, val.array).quantity.check(dimension.dimensionality):
            return val

        raise DimensionalityError(expected=dimension.dimensionality, value=val)

    @classmethod
    def validate_data_type(cls, val: pd.Series, field: ModelField) -> pd.Series:
        if not field.sub_fields or cls._is_physical_dimension(field.sub_fields[0]):
            return val

        data_type = field.sub_fields[0].type_
        if val.dtype == data_type:
            return val

        raise WrongTypeError(expected=data_type, value=val.dtype)

    @classmethod
    def validate_writeable(cls, val: np.ndarray) -> np.ndarray:
        if val.flags.writeable == cls.writeable:
            return val
        raise ArrayWriteableError(expected=cls.writeable, value=val)

    @classmethod
    def _make_iterable_quantity(cls, val: Any):
        if isinstance(val, Quantity) and not isinstance(val.magnitude, Iterable):
            val = Quantity([val.m], val.u)
        return val

    @classmethod
    def _is_physical_dimension(cls, field: ModelField) -> bool:
        return field.type_ == Any or issubclass(field.type_, PhysicalDimension)


if TYPE_CHECKING:
    SeriesLike = pd.Series
    DatetimeSeries = pd.Series
    TimedeltaSeries = pd.Series

else:

    class SeriesLike(ConstrainedSeries[T]):
        strict = False

    class DatetimeSeries(ConstrainedSeries[T]):
        strict = False
        index_type = DatetimeIndex

    class TimedeltaSeries(ConstrainedSeries[T]):
        strict = False
        index_type = TimedeltaIndex
