from dataclasses import dataclass
from typing import Callable, Generic, Set, TypeVar

from .identifiable import EnsureIdentifiable
from .mention import AbstractNodeMention

_ST = TypeVar('_ST', bound=AbstractNodeMention)
_TT = TypeVar('_TT', bound=AbstractNodeMention)


@dataclass(frozen=True)
class AbstractNodeLink(EnsureIdentifiable, Generic[_ST, _TT]):
    source: _ST
    target: _TT

    @classmethod
    def constant_fields(cls) -> Set[str]:
        return {'source', 'target'}

    @staticmethod
    def source_filter(filter_: Callable[[_ST], bool]) -> Callable[['AbstractNodeLink'], bool]:
        def _filter(fact: AbstractNodeLink) -> bool:
            return filter_(fact.source)

        return _filter

    @staticmethod
    def target_filter(filter_: Callable[[_TT], bool]) -> Callable[['AbstractNodeLink'], bool]:
        def _filter(fact: AbstractNodeLink) -> bool:
            return filter_(fact.target)

        return _filter
