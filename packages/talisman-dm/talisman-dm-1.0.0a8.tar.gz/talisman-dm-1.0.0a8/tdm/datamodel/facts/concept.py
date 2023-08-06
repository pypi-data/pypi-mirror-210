from abc import ABCMeta
from dataclasses import dataclass, replace
from typing import Callable, Optional, Sequence, Set, Tuple, Union

from tdm.abstract.datamodel import AbstractDomain, AbstractFact, FactStatus, Identifiable
from tdm.abstract.json_schema import generate_model
from tdm.datamodel.domain import ConceptType


@dataclass(frozen=True)
class ConceptValue(object):
    concept: str
    confidence: Optional[float] = None

    def __post_init__(self):
        if self.confidence is not None and not 0 < self.confidence <= 1:
            raise ValueError(f"value confidence should be in interval (0; 1], {self.confidence} is given")

    @classmethod
    def build(cls, value: Union[str, 'ConceptValue']) -> 'ConceptValue':
        if isinstance(value, ConceptValue):
            return value
        if isinstance(value, str):
            return cls(concept=value)
        raise ValueError


@dataclass(frozen=True)
class _ConceptFact(AbstractFact, metaclass=ABCMeta):  # not an error as id argument is kw only
    type_id: Union[str, ConceptType]
    value: Union[ConceptValue, Tuple[ConceptValue, ...]] = tuple()

    def __post_init__(self):
        if not isinstance(self.type_id, str) and not isinstance(self.type_id, ConceptType):
            raise ValueError(f"concept fact type id conflict: {self.type_id}")

        if isinstance(self.value, str):
            object.__setattr__(self, 'value', ConceptValue.build(self.value))
        elif isinstance(self.value, Sequence):
            object.__setattr__(self, 'value', tuple(map(ConceptValue.build, self.value)))
        else:
            object.__setattr__(self, 'value', ConceptValue.build(self.value))

        if self.status is FactStatus.NEW and isinstance(self.value, ConceptValue):
            object.__setattr__(self, 'value', (self.value,))  # replace with tuple
        elif self.status is FactStatus.APPROVED and isinstance(self.value, tuple):
            if len(self.value) != 1:
                raise ValueError(f"approved fact {self} should have single value")
            object.__setattr__(self, 'value', self.value[0])

    @classmethod
    def constant_fields(cls) -> Set[str]:
        return {'type_id'}


@generate_model(label='concept')
@dataclass(frozen=True)
class ConceptFact(Identifiable, _ConceptFact):

    def replace_with_domain(self, domain: AbstractDomain) -> 'ConceptFact':
        if isinstance(self.type_id, str):
            domain_type = domain.get_type(self.type_id)
            if not isinstance(domain_type, ConceptType):
                raise ValueError
            return replace(self, type_id=domain_type)
        return self

    def _as_tuple(self) -> tuple:
        return self.id, (self.type_id if isinstance(self.type_id, str) else self.type_id.id), self.value

    def __eq__(self, other):
        if not isinstance(other, ConceptFact):
            return NotImplemented
        return self._as_tuple() == other._as_tuple()

    def __hash__(self):
        return hash(self._as_tuple())

    @staticmethod
    def empty_value_filter() -> Callable[['ConceptFact'], bool]:
        return lambda f: isinstance(f.value, tuple) and not f.value

    @staticmethod
    def tuple_value_filter() -> Callable[['ConceptFact'], bool]:
        return lambda f: isinstance(f.value, tuple)

    @staticmethod
    def single_value_filter() -> Callable[['ConceptFact'], bool]:
        return lambda f: isinstance(f.value, ConceptValue)
