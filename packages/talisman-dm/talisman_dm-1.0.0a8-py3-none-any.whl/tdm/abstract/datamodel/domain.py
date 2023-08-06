from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from typing import Callable, Dict, Generic, Iterable, Iterator, Set, Type, TypeVar, Union

from .identifiable import EnsureIdentifiable, Identifiable
from ...helper import generics_mapping, unfold_union


@dataclass(frozen=True)
class AbstractDomainType(EnsureIdentifiable):
    name: str

    @classmethod
    def constant_fields(cls) -> Set[str]:
        return set()


_ST = TypeVar('_ST', bound=AbstractDomainType)
_TT = TypeVar('_TT', bound=AbstractDomainType)


@dataclass(frozen=True)
class AbstractLinkDomainType(AbstractDomainType, Generic[_ST, _TT], metaclass=ABCMeta):
    source: _ST
    target: _TT

    def __post_init__(self):
        types_mapping = generics_mapping(type(self))
        if not isinstance(self.source, unfold_union(types_mapping.get(_ST))):
            raise ValueError(f"Illegal source for {type(self)}. Expected: {types_mapping.get(_ST)}, actual: {type(self.source)}")
        if not isinstance(self.target, unfold_union(types_mapping.get(_TT))):
            raise ValueError(f"Illegal target for {type(self)}. Expected: {types_mapping.get(_TT)}, actual: {type(self.target)}")

    @classmethod
    def constant_fields(cls) -> Set[str]:
        return {'source', 'target'}


_DomainType = TypeVar('_DomainType', bound=AbstractDomainType)


class AbstractDomain(metaclass=ABCMeta):
    __slots__ = ()

    @property
    @abstractmethod
    def id2type(self) -> Dict[str, AbstractDomainType]:
        pass

    @property
    @abstractmethod
    def types(self) -> Dict[Type[AbstractDomainType], Iterable[AbstractDomainType]]:
        pass

    @abstractmethod
    def get_type(self, id_: str) -> AbstractDomainType:
        pass

    @abstractmethod
    def get_types(
            self, type_: Type[_DomainType] = AbstractDomainType, *,
            filter_: Union[Callable[[_DomainType], bool], Iterable[Callable[[_DomainType], bool]]] = tuple()
    ) -> Iterator[_DomainType]:
        pass

    @abstractmethod
    def related_types(
            self, obj: Union[Identifiable, str], type_: Type[_DomainType] = AbstractDomainType, *,
            filter_: Union[Callable[[_DomainType], bool], Iterable[Callable[[_DomainType], bool]]] = tuple()
    ):
        pass
