from itertools import chain
from typing import Any, Dict, Iterable

from tdm.abstract.datamodel import AbstractFact, FactStatus
from tdm.datamodel.facts import AtomValueFact, ConceptFact, PropertyFact, RelationFact
from tdm.datamodel.facts.concept import ConceptValue
from tdm.datamodel.values import DoubleValue, IntValue, StringValue


def get_metadata_facts(doc_id: str, metadata: Dict[str, Any]) -> Iterable[AbstractFact]:
    document_fact = ConceptFact(FactStatus.APPROVED, "document", ConceptValue(doc_id))
    result = [document_fact]
    metadata = metadata
    if not metadata:
        return result
    if 'parent_uuid' in metadata:
        result.append(
            RelationFact(
                FactStatus.APPROVED, "parent", document_fact,
                ConceptFact(FactStatus.APPROVED, "document", ConceptValue(metadata.pop('parent_uuid')))
            )
        )
    for key, value in metadata.items():
        value_facts = generate_value(value)
        result.extend(
            PropertyFact(FactStatus.APPROVED, key, document_fact, value_fact) for value_fact in value_facts
        )
    return result


def generate_value(val: Any) -> Iterable[AtomValueFact]:
    if isinstance(val, int):
        return AtomValueFact(FactStatus.APPROVED, 'int', IntValue(val)),
    if isinstance(val, str):
        return AtomValueFact(FactStatus.APPROVED, 'str', StringValue(val)),
    if isinstance(val, float):
        return AtomValueFact(FactStatus.APPROVED, 'float', DoubleValue(val)),
    if isinstance(val, Iterable):
        return tuple(chain.from_iterable(generate_value(v) for v in val))
    raise ValueError
