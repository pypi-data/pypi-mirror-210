from abc import ABCMeta
from dataclasses import dataclass, replace
from typing import Callable, Sequence, Set, Tuple, Union

from tdm.abstract.datamodel import AbstractDomain, AbstractFact, FactStatus, Identifiable
from tdm.abstract.datamodel.value import AbstractValue
from tdm.abstract.json_schema import generate_model
from tdm.datamodel.domain import AtomValueType, CompositeValueType


@dataclass(frozen=True)
class _AtomValueFact(AbstractFact, metaclass=ABCMeta):
    type_id: Union[str, AtomValueType]
    # tuple is in first place due to strange pydantic bug ((AbstractValue,) is treated as AbstractValue)
    value: Union[Tuple[AbstractValue, ...], AbstractValue] = tuple()

    def __post_init__(self):
        if not isinstance(self.type_id, str) and not isinstance(self.type_id, AtomValueType):
            raise ValueError(f"Illegal type id {self.type_id}, {AtomValueType} is expected")
        value_type = self.type_id.value_type if isinstance(self.type_id, AtomValueType) else AbstractValue

        if isinstance(self.value, Sequence) and not isinstance(self.value, value_type):  # value could implement Sequence?
            if any(not isinstance(v, value_type) for v in self.value):
                raise ValueError(f"Atom value fact {self} value should be {value_type} or tuple of {value_type}")
            object.__setattr__(self, 'value', tuple(self.value))
        elif not isinstance(self.value, value_type):
            raise ValueError(f"Atom value fact {self} value should be value or tuple of value")

        if self.status is FactStatus.NEW and isinstance(self.value, AbstractValue):
            object.__setattr__(self, 'value', (self.value,))
        elif self.status is FactStatus.APPROVED and isinstance(self.value, tuple):
            if len(self.value) != 1 or not isinstance(self.value[0], value_type):
                raise ValueError(f"approved fact {self} should have single value")
            object.__setattr__(self, 'value', self.value[0])

    @classmethod
    def constant_fields(cls) -> Set[str]:
        return {'type_id'}


@generate_model(label='atom')
@dataclass(frozen=True)
class AtomValueFact(Identifiable, _AtomValueFact):

    def replace_with_domain(self, domain: AbstractDomain) -> 'AtomValueFact':
        if isinstance(self.type_id, str):
            domain_type = domain.get_type(self.type_id)
            if not isinstance(domain_type, AtomValueType):
                raise ValueError
            return replace(self, type_id=domain_type)
        return self

    def _as_tuple(self) -> tuple:
        return self.id, (self.type_id if isinstance(self.type_id, str) else self.type_id.id), self.value

    def __eq__(self, other):
        if not isinstance(other, AtomValueFact):
            return NotImplemented
        return self._as_tuple() == other._as_tuple()

    def __hash__(self):
        return hash(self._as_tuple())

    @staticmethod
    def empty_value_filter() -> Callable[['AtomValueFact'], bool]:
        return lambda f: isinstance(f.value, tuple) and not f.value

    @staticmethod
    def tuple_value_filter() -> Callable[['AtomValueFact'], bool]:
        return lambda f: isinstance(f.value, tuple)

    @staticmethod
    def single_value_filter() -> Callable[['AtomValueFact'], bool]:
        return lambda f: isinstance(f.value, AbstractValue)


@dataclass(frozen=True)
class _CompositeValueFact(AbstractFact, metaclass=ABCMeta):
    type_id: Union[str, CompositeValueType]

    @classmethod
    def constant_fields(cls) -> Set[str]:
        return {'type_id'}


@generate_model(label='composite')
@dataclass(frozen=True)
class CompositeValueFact(Identifiable, _CompositeValueFact):

    def replace_with_domain(self, domain: AbstractDomain) -> 'CompositeValueFact':
        if isinstance(self.type_id, str):
            domain_type = domain.get_type(self.type_id)
            if not isinstance(domain_type, CompositeValueType):
                raise ValueError
            return replace(self, type_id=domain_type)
        return self

    def _as_tuple(self) -> tuple:
        return self.id, (self.type_id if isinstance(self.type_id, str) else self.type_id.id)

    def __eq__(self, other):
        if not isinstance(other, CompositeValueFact):
            return NotImplemented
        return self._as_tuple() == other._as_tuple()

    def __hash__(self):
        return hash(self._as_tuple())
