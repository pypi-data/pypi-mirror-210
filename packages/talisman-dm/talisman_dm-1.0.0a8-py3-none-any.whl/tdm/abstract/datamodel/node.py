from dataclasses import dataclass, field
from typing import Generic, Set, TypeVar

from tdm.helper import generics_mapping
from .identifiable import Identifiable
from .markup import AbstractMarkup, FrozenMarkup


@dataclass(frozen=True)
class BaseNodeMetadata:
    hidden: bool = False


_NodeMetadata = TypeVar("_NodeMetadata", bound=BaseNodeMetadata)


@dataclass(frozen=True)
class AbstractNode(Identifiable, Generic[_NodeMetadata]):
    metadata: _NodeMetadata = None
    markup: AbstractMarkup = field(default_factory=FrozenMarkup, hash=False)

    def __post_init__(self):
        super().__post_init__()
        if self.metadata is None:
            # hack for runtime metadata generation (if no value passed)
            object.__setattr__(self, 'metadata', self._generate_metadata())
        object.__setattr__(self, 'markup', self._convert_markup(self.markup))

    def _convert_markup(self, markup: AbstractMarkup) -> AbstractMarkup:
        if not isinstance(markup, AbstractMarkup):
            raise ValueError
        return markup

    def _generate_metadata(self) -> _NodeMetadata:
        type_vars = generics_mapping(type(self))
        return type_vars[_NodeMetadata]()

    @classmethod
    def constant_fields(cls) -> Set[str]:
        return set()


_Content = TypeVar('_Content')


@dataclass(frozen=True)
class _AbstractContentNode(Generic[_Content]):
    content: _Content


@dataclass(frozen=True)
class AbstractContentNode(AbstractNode[_NodeMetadata], _AbstractContentNode[_Content], Generic[_NodeMetadata, _Content]):

    @classmethod
    def constant_fields(cls) -> Set[str]:
        return {'content'}
