from typing import TYPE_CHECKING, Any, Type

import pandas as pd
from pandas import DatetimeIndex, Index, TimedeltaIndex
from pydantic.fields import ModelField

from optool.fields.util import get_type_validator


class IndexTypeError(ValueError):

    def __init__(self, *, expected: Type[Index], value: pd.DataFrame) -> None:
        super().__init__(f"expected index type {expected}, but got a DataFrame with index type {type(value.index)}")


class ConstrainedDataFrame(pd.DataFrame):
    """
    Pydantic-compatible field type for :py:class:`pandas.DataFrame` objects, which allows to specify the index type.

    See Also:
        `Pydantic documentation: Custom Data Types <https://docs.pydantic.dev/usage/types/#custom-data-types>`_ and
        class :py:class:`pydantic.types.ConstrainedInt` or similar of :py:mod:`pydantic`
    """

    strict: bool = True
    index_type: Type[Index] = pd.RangeIndex

    @classmethod
    def __get_validators__(cls):
        yield get_type_validator(pd.DataFrame) if cls.strict else cls.validate_dataframe
        yield cls.validate_index_type

    @classmethod
    def validate_dataframe(cls, val: Any, field: ModelField) -> pd.DataFrame:
        if isinstance(val, pd.DataFrame):
            return val
        if field.sub_fields:
            raise TypeError(f"A constrained DataFrame cannot by typed, but have sub-fields {field.sub_fields}")

        return pd.DataFrame(val)

    @classmethod
    def validate_index_type(cls, val: pd.DataFrame, field: ModelField) -> pd.DataFrame:
        if cls.index_type is None or isinstance(val.index, cls.index_type):
            return val
        raise IndexTypeError(expected=cls.index_type, value=val)


if TYPE_CHECKING:
    DataFrameLike = pd.DataFrame
    DatetimeDataFrame = pd.DataFrame
    TimedeltaDataFrame = pd.DataFrame

else:

    class DataFrameLike(ConstrainedDataFrame):
        strict = False

    class DatetimeDataFrame(ConstrainedDataFrame):
        strict = False
        index_type = DatetimeIndex

    class TimedeltaDataFrame(ConstrainedDataFrame):
        strict = False
        index_type = TimedeltaIndex
