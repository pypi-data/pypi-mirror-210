from __future__ import annotations

from datetime import datetime
from typing import Any, Dict
from zoneinfo import ZoneInfo

from optool.serialization import AllowedSerializedDictKeys, Serializer


class ZoneInfoSerializer(Serializer[ZoneInfo]):

    def serialize(self, obj: ZoneInfo) -> Dict[AllowedSerializedDictKeys, Any]:
        return {'key': obj.key}

    def deserialize(self, raw: Dict[AllowedSerializedDictKeys, Any]) -> ZoneInfo:
        return ZoneInfo(raw['key'])


class DatetimeSerializer(Serializer[datetime]):
    _DICT_KEY_VALUE = 'value'
    _DICT_KEY_TIMEZONE = 'timezone'
    _DICT_KEY_FORMAT = 'format'
    _DATE_FMT = "%Y-%m-%d %H:%M:%S.%f"
    _DATE_FMT_TZ = _DATE_FMT + " %z"

    def serialize(self, obj: datetime) -> Dict[AllowedSerializedDictKeys, Any]:
        date_fmt = self._DATE_FMT_TZ if obj.tzinfo else self._DATE_FMT
        return {
            self._DICT_KEY_VALUE: obj.strftime(date_fmt),
            self._DICT_KEY_FORMAT: date_fmt,
            self._DICT_KEY_TIMEZONE: obj.tzinfo,
        }

    def deserialize(self, raw: Dict[AllowedSerializedDictKeys, Any]) -> datetime:
        obj = datetime.strptime(raw[self._DICT_KEY_VALUE], raw[self._DICT_KEY_FORMAT])
        if tz_info := raw[self._DICT_KEY_TIMEZONE]:
            obj = obj.astimezone(tz_info)
        return obj
