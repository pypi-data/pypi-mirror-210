from dataclasses import dataclass
from typing import Optional

from tdm.abstract.datamodel.value import AbstractValue, EnsureConfidenced
from tdm.abstract.json_schema import generate_model


@dataclass(frozen=True)
class Date(object):
    year: Optional[int] = None
    month: Optional[int] = None
    day: Optional[int] = None


@dataclass(frozen=True)
class Time(object):
    hour: int
    minute: int
    second: int


@dataclass(frozen=True)
class _DateTimeValue(EnsureConfidenced):
    date: Date
    time: Optional[Time] = None


@generate_model
@dataclass(frozen=True)
class DateTimeValue(AbstractValue, _DateTimeValue):

    @classmethod
    def from_dict(cls, value: dict) -> 'DateTimeValue':
        args = {
            'date': Date(**value['date'])
        }
        if 'time' in value:
            args['time'] = Time(**value['time'])
        return cls(**args)
