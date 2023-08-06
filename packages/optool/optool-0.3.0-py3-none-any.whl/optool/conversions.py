from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from pandas import DatetimeIndex

from optool.uom import UNITS, Quantity


def datetime_index_to_samples(timestamps: DatetimeIndex) -> Quantity:
    duration = (timestamps - timestamps[0]).to_pytimedelta()
    sample_times_seconds = np.array([val.total_seconds() for val in duration])
    return Quantity(sample_times_seconds, UNITS.second)


def datetime_index_to_intervals(timestamps: DatetimeIndex) -> Quantity:
    intervals_seconds = np.diff(timestamps.astype(np.int64)) / 10**9
    return Quantity(intervals_seconds, UNITS.second)


def samples_to_datetime_index(start: datetime, sample_times: Quantity) -> DatetimeIndex:
    sample_times_seconds = sample_times.m_as(UNITS.second)
    duration = [timedelta(0, float(second)) for second in sample_times_seconds]
    datetime_values = [start + val for val in duration]
    return pd.DatetimeIndex(datetime_values)
