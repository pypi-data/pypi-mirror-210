from abc import abstractmethod
from typing import Generic, Type, TypeVar

from tdm.abstract.datamodel import AbstractNode

_Node = TypeVar('_Node', bound=AbstractNode)
_AbstractNodeWrapper = TypeVar('_AbstractNodeWrapper', bound='AbstractNodeWrapper')


class AbstractNodeWrapper(AbstractNode, Generic[_Node]):
    @classmethod
    @abstractmethod
    def wrap(cls: Type[_AbstractNodeWrapper], node: _Node) -> _AbstractNodeWrapper:
        pass
