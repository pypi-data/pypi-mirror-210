from dataclasses import dataclass

from tdm.abstract.datamodel.value import AbstractValue, EnsureConfidenced
from tdm.abstract.json_schema import generate_model


@dataclass(frozen=True)
class _LinkValue(EnsureConfidenced):
    link: str


@generate_model
@dataclass(frozen=True)
class LinkValue(AbstractValue, _LinkValue):
    pass
