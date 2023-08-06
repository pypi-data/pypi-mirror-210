from abc import ABCMeta, abstractmethod
from dataclasses import dataclass, replace
from enum import Enum
from functools import total_ordering
from typing import Callable, Generic, Iterable, Optional, Set, Type, TypeVar, Union

from tdm.helper import generics_mapping, unfold_union
from .domain import AbstractDomain, AbstractDomainType, AbstractLinkDomainType
from .identifiable import EnsureIdentifiable


@total_ordering
class FactStatus(str, Enum):
    def __new__(cls, name: str, priority: int):
        obj = str.__new__(cls, name)
        obj._value_ = name
        obj.priority = priority
        return obj

    APPROVED = ("approved", 0)
    DECLINED = ("declined", 1)
    AUTO = ("auto", 2)
    HIDDEN = ("hidden", 3)
    NEW = ("new", 4)

    def __lt__(self, other: 'FactStatus'):
        if not isinstance(other, FactStatus):
            return NotImplemented
        return self.priority < other.priority


_Fact = TypeVar('_Fact', bound='AbstractFact')


@dataclass(frozen=True)
class AbstractFact(EnsureIdentifiable, metaclass=ABCMeta):
    status: FactStatus

    @abstractmethod
    def replace_with_domain(self: _Fact, domain: AbstractDomain) -> _Fact:
        pass

    @staticmethod
    def id_filter(obj: Union['AbstractFact', str]) -> Callable[['AbstractFact'], bool]:
        id_ = obj.id if isinstance(obj, AbstractFact) else obj

        def _filter(fact: AbstractFact) -> bool:
            return fact.id == id_

        return _filter

    @staticmethod
    def status_filter(status: Union[FactStatus, Iterable[FactStatus]]) -> Callable[['AbstractFact'], bool]:
        if isinstance(status, FactStatus):
            def _filter(fact: AbstractFact) -> bool:
                return fact.status is status
        else:
            statuses = frozenset(status)

            def _filter(fact: AbstractFact) -> bool:
                return fact.status in statuses

        return _filter

    @staticmethod
    def type_filter(type_: Type['AbstractFact']) -> Callable[['AbstractFact'], bool]:
        def _filter(fact: AbstractFact) -> bool:
            return isinstance(fact, type_)

        return _filter


_ST = TypeVar('_ST', bound=AbstractFact)
_TT = TypeVar('_TT', bound=AbstractFact)
_LDT = TypeVar('_LDT', bound=AbstractLinkDomainType)

_LinkFact = TypeVar('_LinkFact', bound='AbstractLinkFact')


@dataclass(frozen=True)
class AbstractLinkFact(AbstractFact, Generic[_ST, _TT, _LDT], metaclass=ABCMeta):
    type_id: Union[str, _LDT]
    source: _ST
    target: _TT
    value: Optional[str] = None

    def replace_with_domain(self: _LinkFact, domain: AbstractDomain) -> _LinkFact:
        domain_type = generics_mapping(type(self)).get(_LDT)
        type_id = domain.get_type(self.type_id) if isinstance(self.type_id, str) else self.type_id
        if not isinstance(type_id, domain_type):
            raise ValueError

        source = self.source.replace_with_domain(domain)
        target = self.target.replace_with_domain(domain)

        if self.type_id is type_id and self.source is source and self.target is target:
            return self
        return replace(self, type_id=type_id, source=source, target=target)

    def _as_tuple(self) -> tuple:
        return self.id, (self.type_id if isinstance(self.type_id, str) else self.type_id.id), self.source, self.target, self.value

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        return self._as_tuple() == other._as_tuple()

    def __hash__(self):
        return hash(self._as_tuple())

    def __post_init__(self):
        mapping = generics_mapping(type(self))
        if not isinstance(self.type_id, str):
            domain_type = mapping.get(_LDT)
            if not issubclass(domain_type, AbstractLinkDomainType):
                raise ValueError
            if not isinstance(self.type_id, domain_type):
                raise ValueError(f"illegal type id for fact {self}. {domain_type} is expected")
            self._check_argument(self.type_id.source, self.source.type_id)
            self._check_argument(self.type_id.target, self.target.type_id)
        if not isinstance(self.source, unfold_union(mapping.get(_ST))):
            raise ValueError(f"illegal source fact: {self.source}, {mapping.get(_ST)} is expected")
        if not isinstance(self.target, unfold_union(mapping.get(_TT))):
            raise ValueError(f"illegal target fact: {self.target}, {mapping.get(_TT)} is expected")

    @staticmethod
    def _check_argument(expected_type: AbstractDomainType, actual_type: Union[str, AbstractDomainType]) -> None:
        if isinstance(actual_type, str) and expected_type.id != actual_type:
            raise ValueError
        elif isinstance(actual_type, AbstractDomainType) and expected_type != actual_type:
            raise ValueError

    @classmethod
    def constant_fields(cls) -> Set[str]:
        return {'source', 'target', 'type_id'}

    @staticmethod
    def type_id_filter(type_id: Union[str, Iterable[str]]) -> Callable[['AbstractLinkFact'], bool]:
        if isinstance(type_id, str):
            def _filter(fact: AbstractLinkFact) -> bool:
                return fact.type_id == type_id
        else:
            type_ids = frozenset(type_id)

            def _filter(fact: AbstractLinkFact) -> bool:
                return fact.type_id in type_ids

        return _filter

    @staticmethod
    def source_filter(filter_: Callable[[_ST], bool]) -> Callable[['AbstractLinkFact'], bool]:
        def _filter(fact: AbstractLinkFact) -> bool:
            return filter_(fact.source)

        return _filter

    @staticmethod
    def target_filter(filter_: Callable[[_TT], bool]) -> Callable[['AbstractLinkFact'], bool]:
        def _filter(fact: AbstractLinkFact) -> bool:
            return filter_(fact.target)

        return _filter
