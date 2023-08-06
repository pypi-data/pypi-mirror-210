from collections import defaultdict
from typing import ClassVar, Dict, Optional, Tuple, Type

from pydantic import BaseModel

from tdm.abstract.datamodel import AbstractDomain, AbstractFact, AbstractValue, TalismanDocument
from tdm.datamodel.document import TalismanDocumentFactory
from tdm.legacy import DocumentMetadataModel
from .content import TreeDocumentContentModel
from .convert import build_structure, convert_concept_fact, convert_property_fact, convert_relation_fact, convert_value_fact, \
    get_metadata_facts
from .directive import DirectiveModel
from .fact import ConceptFactModel, FactModel, FactType, PropertyFactModel, RelationFactModel, ValueFactModel


class TalismanDocumentModel(BaseModel):
    _DEFAULT_DOMAIN: ClassVar[AbstractDomain] = None
    _domain: AbstractDomain = None

    id: str
    content: TreeDocumentContentModel
    metadata: Optional[DocumentMetadataModel]
    facts: Optional[Tuple[FactModel, ...]]  # pydantic fails to serialize FrozenSet[FactModel]
    directives: Optional[Tuple[DirectiveModel, ...]]

    @classmethod
    def set_default_domain(cls, domain: Optional[AbstractDomain]) -> None:
        cls._DEFAULT_DOMAIN = domain

    def set_domain(self, domain: Optional[AbstractDomain]) -> None:
        self._domain = domain

    def to_doc(self, titles: Dict[str, Tuple[str, str]], value_types: Dict[str, Type[AbstractValue]]) -> TalismanDocument:
        result = TalismanDocumentFactory(self._domain or self._DEFAULT_DOMAIN).create_document(id_=self.id)

        nodes, structure, node_links = build_structure(self.content)
        result = result.with_nodes(nodes).with_structure(structure).with_node_links(node_links, update=True).with_main_root(self.content.id)

        # convert document metadata to facts
        metadata = self.metadata.to_metadata() if self.metadata else {}
        result = result.with_metadata(metadata).with_facts(get_metadata_facts(self.id, metadata), update=True)

        # now convert facts
        old_facts = defaultdict(set)
        for fact in (self.facts or []):
            old_facts[fact.fact_type].add(fact)

        facts = []
        facts_mapping: dict[str, AbstractFact] = {}

        # start with concept facts
        # old concept fact consists of <status, type_id, value, mention> and should be converted to chain
        # ConceptFact(type_id) <- Property(Name) -> AtomValueFact(value) <-  MentionFact -> TextNodeMention(mention)
        for old_concept_fact in old_facts.get(FactType.CONCEPT, []):
            old_concept_fact: ConceptFactModel
            concept_fact, *other = convert_concept_fact(old_concept_fact, result, titles, value_types)
            facts_mapping[old_concept_fact.id] = concept_fact
            facts.extend((concept_fact, *other))

        # then convert ValueFacts
        # old value fact consists of <status, type_id, value, mention> and should be converted to chain
        # AtomValueFact(value) <- MentionFact -> TextNodeMention(mention)
        for old_value_fact in old_facts.get(FactType.VALUE, []):
            old_value_fact: ValueFactModel
            value_fact, *other = convert_value_fact(old_value_fact, result, value_types)
            facts_mapping[old_value_fact.id] = value_fact
            facts.extend((value_fact, *other))

        # now relations
        # old relations should be mapped to new ones with trivial modifications
        for old_relation_fact in old_facts.get(FactType.RELATION, []):
            old_relation_fact: RelationFactModel
            relation_fact = convert_relation_fact(old_relation_fact, facts_mapping)
            facts_mapping[old_relation_fact.id] = relation_fact
            facts.append(relation_fact)

        # and finally properties and relation properties
        for old_property_fact in old_facts.get(FactType.PROPERTY, []):
            old_property_fact: PropertyFactModel
            property_fact = convert_property_fact(old_property_fact, facts_mapping)
            facts.append(property_fact)

        result = result.with_facts(facts, update=True)
        return result
