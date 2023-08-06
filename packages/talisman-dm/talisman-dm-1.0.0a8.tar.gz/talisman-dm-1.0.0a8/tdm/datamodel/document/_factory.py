import uuid
from typing import Any, Dict, Iterable, Optional, Tuple

from tdm.abstract.datamodel import AbstractDirective, AbstractDocumentFactory, AbstractDomain, AbstractFact, AbstractNode, \
    AbstractNodeLink, TalismanDocument
from tdm.datamodel.common import TypedIdsContainer
from tdm.datamodel.domain import get_default_domain
from ._impl import TalismanDocumentImpl
from ._structure import NodesStructure


class TalismanDocumentFactory(AbstractDocumentFactory):

    def __init__(self, domain: Optional[AbstractDomain] = None):
        self._domain = domain if domain is not None else get_default_domain()

    def create_document(self, *, id_: Optional[str] = None) -> TalismanDocument:
        return TalismanDocumentImpl(
            id2view={},
            dependencies={},
            structure=NodesStructure(),
            containers={
                AbstractNode: TypedIdsContainer(AbstractNode, ()),
                AbstractNodeLink: TypedIdsContainer(AbstractNodeLink, ()),
                AbstractFact: TypedIdsContainer(AbstractFact, ()),
                AbstractDirective: TypedIdsContainer(AbstractDirective, ())
            },
            metadata=None,
            id_=id_ or self.generate_id(),
            domain=self._domain
        )

    def construct(
            self,
            content: Iterable[AbstractNode] = (),
            structure: Dict[str, Tuple[str, ...]] = None,
            root: Optional[str] = None,
            node_links: Iterable[AbstractNodeLink] = (),
            facts: Iterable[AbstractFact] = (),
            directives: Iterable[AbstractDirective] = (),
            metadata: Optional[Dict[str, Any]] = None,
            *, id_: Optional[str] = None
    ) -> TalismanDocument:
        doc: TalismanDocumentImpl = self.create_document(id_=id_)
        doc = doc.with_elements((*content, *node_links, *facts, *directives)) \
            .with_structure(structure) \
            .with_main_root(root) \
            .with_metadata(metadata)
        return doc

    @staticmethod
    def generate_id():
        return str(uuid.uuid4())
