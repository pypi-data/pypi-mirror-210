from dataclasses import dataclass
from typing import Set, Type

from tdm.abstract.datamodel import AbstractDomainType, AbstractValue, Identifiable


@dataclass(frozen=True)
class _AtomValueType(AbstractDomainType):
    value_type: Type[AbstractValue]

    @classmethod
    def constant_fields(cls) -> Set[str]:
        return {'value_type'}


@dataclass(frozen=True)
class AtomValueType(Identifiable, _AtomValueType):
    pass
