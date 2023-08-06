from dataclasses import dataclass
from typing import Optional

from tdm.abstract.datamodel.value import AbstractValue, EnsureConfidenced
from tdm.abstract.json_schema import generate_model


@dataclass(frozen=True)
class Coordinates(object):
    latitude: float
    longitude: float


@dataclass(frozen=True)
class _GeoPointValue(EnsureConfidenced):
    point: Optional[Coordinates] = None
    name: Optional[str] = None


@generate_model
@dataclass(frozen=True)
class GeoPointValue(AbstractValue, _GeoPointValue):

    @classmethod
    def from_dict(cls, value: dict) -> 'GeoPointValue':
        args = {}
        if 'point' in value:
            args['point'] = Coordinates(**value['point'])
        if 'name' in value:
            args['name'] = value['name']
        return cls(**args)
