from abc import ABCMeta, abstractmethod
from typing import Any, Callable, Dict, Iterable, Iterator, Optional, Set, Tuple, Type, TypeVar, Union

from .directive import AbstractDirective
from .fact import AbstractFact
from .identifiable import Identifiable
from .link import AbstractNodeLink
from .node import AbstractNode

_TD = TypeVar('_TD', bound='TalismanDocument')
_Fact = TypeVar('_Fact', bound=AbstractFact)
_NodeLink = TypeVar('_NodeLink', bound=AbstractNodeLink)
_Node = TypeVar('_Node', bound=AbstractNode)
_Directive = TypeVar('_Directive', bound=AbstractDirective)

NodeOrId = Union[str, AbstractNode]


class TalismanDocument(metaclass=ABCMeta):
    __slots__ = ()

    @property
    @abstractmethod
    def id(self) -> str:
        pass

    # nodes methods

    @property
    @abstractmethod
    def id2node(self) -> Dict[str, AbstractNode]:
        pass

    @property
    @abstractmethod
    def nodes(self) -> Dict[Type[AbstractNode], Iterable[AbstractNode]]:
        pass

    @abstractmethod
    def get_node(self, id_: str) -> AbstractNode:
        pass

    @abstractmethod
    def get_nodes(
            self, type_: Type[_Node] = AbstractNode, *,
            filter_: Union[Callable[[_Node], bool], Iterable[Callable[[_Node], bool]]] = tuple()
    ) -> Iterator[_Node]:
        pass

    @abstractmethod
    def related_nodes(
            self, obj: Union[Identifiable, str], type_: Type[_Node] = AbstractNode, *,
            filter_: Union[Callable[[_Node], bool], Iterable[Callable[[_Node], bool]]] = tuple()
    ) -> Iterator[_Node]:
        pass

    @abstractmethod
    def with_nodes(self: _TD, nodes: Iterable[AbstractNode]) -> _TD:
        pass

    @abstractmethod
    def without_nodes(self: _TD, nodes: Iterable[NodeOrId], *, cascade: bool = True) -> _TD:
        pass

    # structure methods

    @property
    @abstractmethod
    def roots(self) -> Set[AbstractNode]:
        pass

    @property
    @abstractmethod
    def main_root(self) -> Optional[AbstractNode]:
        pass

    @abstractmethod
    def with_main_root(self: _TD, node: Optional[NodeOrId], *, update: bool = False) -> _TD:
        pass

    @abstractmethod
    def parent(self, node: NodeOrId) -> Optional[AbstractNode]:
        pass

    @abstractmethod
    def child_nodes(self, node: Union[str, AbstractNode]) -> Tuple[AbstractNode, ...]:
        pass

    @abstractmethod
    def with_structure(self: _TD, structure: Dict[NodeOrId, Iterable[NodeOrId]], *, force: bool = False, update: bool = False) -> _TD:
        pass

    @abstractmethod
    def with_node_parent(self: _TD, child: NodeOrId, parent: NodeOrId, *, force: bool = False, update: bool = False) -> _TD:
        pass

    @abstractmethod
    def with_roots(self: _TD, nodes: Iterable[NodeOrId]) -> _TD:
        pass

    @abstractmethod
    def without_structure(self: _TD, structure: Dict[NodeOrId, Iterable[NodeOrId]]) -> _TD:
        pass

    # semantic link methods

    @property
    @abstractmethod
    def id2node_link(self) -> Dict[str, AbstractNodeLink]:
        pass

    @property
    @abstractmethod
    def node_links(self) -> Dict[Type[AbstractNodeLink], Iterable[AbstractNodeLink]]:
        pass

    @abstractmethod
    def get_node_link(self, id_: str) -> AbstractNodeLink:
        pass

    @abstractmethod
    def get_node_links(
            self, type_: Type[_NodeLink] = AbstractNodeLink, *,
            filter_: Union[Callable[[_NodeLink], bool], Iterable[Callable[[_NodeLink], bool]]] = tuple()
    ) -> Iterator[_NodeLink]:
        pass

    @abstractmethod
    def related_node_links(
            self, obj: Union[Identifiable, str], type_: Type[_NodeLink] = AbstractNodeLink, *,
            filter_: Union[Callable[[_NodeLink], bool], Iterable[Callable[[_NodeLink], bool]]] = tuple()
    ) -> Iterator[_NodeLink]:
        pass

    @abstractmethod
    def with_node_links(self: _TD, links: Iterable[AbstractNodeLink], *, update: bool = False) -> _TD:
        pass

    @abstractmethod
    def without_node_links(self: _TD, links: Iterable[Union[str, AbstractNodeLink]], *, cascade: bool = False) -> _TD:
        pass

    # facts methods

    @property
    @abstractmethod
    def id2fact(self) -> Dict[str, AbstractFact]:
        pass

    @property
    @abstractmethod
    def facts(self) -> Dict[Type[AbstractFact], Iterable[AbstractFact]]:
        pass

    @abstractmethod
    def get_fact(self, id_: str) -> AbstractFact:
        pass

    @abstractmethod
    def get_facts(
            self, type_: Type[_Fact] = AbstractFact, *,
            filter_: Union[Callable[[_Fact], bool], Iterable[Callable[[_Fact], bool]]] = tuple()
    ) -> Iterator[_Fact]:
        pass

    @abstractmethod
    def related_facts(
            self, obj: Union[Identifiable, str], type_: Type[_Fact] = AbstractFact, *,
            filter_: Union[Callable[[_Fact], bool], Iterable[Callable[[_Fact], bool]]] = tuple()
    ) -> Iterator[_Fact]:
        pass

    @abstractmethod
    def with_facts(self: _TD, facts: Iterable[AbstractFact], *, update: bool = False) -> _TD:
        pass

    @abstractmethod
    def without_facts(self: _TD, facts: Iterable[Union[str, AbstractFact]], *, cascade: bool = False) -> _TD:
        pass

    # directive methods

    @property
    @abstractmethod
    def id2directive(self) -> Dict[str, AbstractDirective]:
        pass

    @property
    @abstractmethod
    def directives(self) -> Dict[Type[AbstractDirective], Iterable[AbstractDirective]]:
        pass

    @abstractmethod
    def get_directive(self, id_: str) -> AbstractDirective:
        pass

    @abstractmethod
    def get_directives(
            self, type_: Type[_Directive] = AbstractDirective, *,
            filter_: Union[Callable[[_Directive], bool], Iterable[Callable[[_Directive], bool]]] = tuple()
    ) -> Iterator[_Directive]:
        pass

    @abstractmethod
    def related_directives(
            self, obj: Union[Identifiable, str], type_: Type[_Directive] = AbstractDirective, *,
            filter_: Union[Callable[[_Directive], bool], Iterable[Callable[[_Directive], bool]]] = tuple()
    ) -> Iterator[_Directive]:
        pass

    @abstractmethod
    def with_directives(self: _TD, directives: Iterable[AbstractDirective], *, update: bool = False) -> _TD:
        pass

    @abstractmethod
    def without_directives(self: _TD, directives: Iterable[Union[str, AbstractDirective]], *, cascade: bool = False) -> _TD:
        pass

    # metadata methods

    @property
    @abstractmethod
    def metadata(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def with_metadata(self: _TD, metadata: Dict[str, Any]) -> _TD:
        pass


class AbstractDocumentFactory(metaclass=ABCMeta):
    @abstractmethod
    def create_document(self, *, id_: Optional[str] = None) -> TalismanDocument:
        pass
