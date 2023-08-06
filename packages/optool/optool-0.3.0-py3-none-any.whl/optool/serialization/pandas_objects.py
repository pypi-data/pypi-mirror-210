from __future__ import annotations

from datetime import datetime
from typing import Any, Dict

import pandas as pd
from pint_pandas import PintArray

from optool.serialization import AllowedSerializedDictKeys, Serializer


class PandasRangeIndexSerializer(Serializer[pd.RangeIndex]):

    def serialize(self, obj: pd.RangeIndex) -> Dict[AllowedSerializedDictKeys, Any]:
        return dict(start=obj.start, stop=obj.stop, step=obj.step, name=obj.name)

    def deserialize(self, raw: Dict[AllowedSerializedDictKeys, Any]) -> pd.RangeIndex:
        return pd.RangeIndex(**raw)


class PandasDatetimeIndexSerializer(Serializer[pd.DatetimeIndex]):
    _DICT_KEY_VALUES = 'values'
    _DICT_KEY_FORMAT = 'format'
    _DICT_KEY_FREQUENCY = 'freq'
    _DICT_KEY_TIMEZONE = 'timezone'
    _DATE_FMT = "%Y-%m-%d %H:%M:%S.%f"
    _DATE_FMT_TZ = _DATE_FMT + " %z"

    def serialize(self, obj: pd.DatetimeIndex) -> Dict[AllowedSerializedDictKeys, Any]:
        date_fmt = self._DATE_FMT_TZ if obj.tzinfo else self._DATE_FMT
        return {
            self._DICT_KEY_VALUES: obj.strftime(date_fmt).to_list(),
            self._DICT_KEY_FORMAT: date_fmt,
            self._DICT_KEY_FREQUENCY: obj.freqstr,
            self._DICT_KEY_TIMEZONE: obj.tzinfo,
        }

    def deserialize(self, raw: Dict[AllowedSerializedDictKeys, Any]) -> pd.DatetimeIndex:
        date_fmt = raw[self._DICT_KEY_FORMAT]
        dt_array = [datetime.strptime(item, date_fmt) for item in raw[self._DICT_KEY_VALUES]]

        if tz_info := raw[self._DICT_KEY_TIMEZONE]:
            dt_array = [item.astimezone(tz_info) for item in dt_array]

        obj = pd.DatetimeIndex(dt_array)

        if freq := raw[self._DICT_KEY_FREQUENCY]:
            obj.freq = freq

        return obj


class PandasSeriesSerializer(Serializer[pd.Series]):

    def serialize(self, obj: pd.Series) -> Dict[AllowedSerializedDictKeys, Any]:
        if obj.ndim != 1:
            raise ValueError(f"The number of dimensions of a pandas series must be 1, but is {obj.ndim}.")
        return dict(name=obj.name, index=obj.index, data=obj.values)

    def deserialize(self, raw: Dict[AllowedSerializedDictKeys, Any]) -> pd.Series:
        return pd.Series(**raw)


class PandasDataFrameSerializer(Serializer[pd.DataFrame]):
    _DICT_KEY_INDEX = '__index__'

    def serialize(self, obj: pd.DataFrame) -> Dict[AllowedSerializedDictKeys, Any]:
        columns_dict = obj.to_dict(orient='list')
        for key in columns_dict:
            if isinstance(obj[key].values, PintArray):
                columns_dict[key] = obj[key].values
        return {self._DICT_KEY_INDEX: obj.index, **columns_dict}

    def deserialize(self, raw: Dict[AllowedSerializedDictKeys, Any]) -> pd.DataFrame:
        index = raw.pop(self._DICT_KEY_INDEX)
        obj = pd.DataFrame.from_dict(raw, orient='columns')
        obj.index = index
        return obj
