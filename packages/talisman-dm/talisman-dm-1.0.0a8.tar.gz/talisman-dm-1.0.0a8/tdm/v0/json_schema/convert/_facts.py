from operator import attrgetter
from typing import Dict, Iterator, Optional, Sequence, Tuple, Type, Union

from tdm.abstract.datamodel import AbstractFact, AbstractValue, FactStatus, Identifiable, TalismanDocument
from tdm.datamodel.facts import AtomValueFact, ConceptFact, MentionFact, PropertyFact, RelationFact, RelationPropertyFact
from tdm.datamodel.facts.concept import ConceptValue
from tdm.datamodel.mentions import TextNodeMention
from tdm.datamodel.nodes import TextNode
from tdm.datamodel.values import StringValue
from tdm.v0.json_schema.fact import AbstractFactModel, ConceptFactModel, PropertyFactModel, RelationFactModel, ValueFactModel


def _fact_text(fact: AbstractFactModel) -> Optional[str]:
    if fact.metadata is not None and hasattr(fact.metadata, 'text'):
        return ' '.join(fact.metadata.text)
    if fact.mention:
        return ' '.join(map(attrgetter('value'), fact.mention))
    return None


def convert_concept_fact(
        fact: ConceptFactModel, doc: TalismanDocument, titles: Dict[str, Tuple[str, str]], value_types: Dict[str, Type[AbstractValue]]
) -> Iterator[AbstractFact]:
    status = FactStatus(fact.status.value)
    if isinstance(fact.value, str):
        value = ConceptValue(fact.value)
    elif isinstance(fact.value, Sequence):
        value = tuple(ConceptValue(v) for v in fact.value)
    else:
        raise ValueError(f"illegal concept fact value {fact.value}")
    concept_fact = ConceptFact(
        status=status,
        type_id=fact.type_id,
        value=value,
        id=fact.id  # preserve old id
    )
    yield concept_fact
    name = _fact_text(fact)
    if not name:
        return
    property_type_id, value_type_id = titles[fact.type_id]
    if value_types[value_type_id] is not StringValue:
        raise ValueError
    old_fashion_value = ValueFactModel(
        id=Identifiable.generate_id(),
        status=fact.status,
        type_id=value_type_id,
        value={'value': name},
        mention=fact.mention,
        metadata=fact.metadata
    )
    value, *other = convert_value_fact(old_fashion_value, doc, value_types)
    yield value
    yield from other
    yield PropertyFact(
        status=status,
        type_id=property_type_id,
        source=concept_fact,
        target=value
    )


def convert_value_fact(fact: ValueFactModel, doc: TalismanDocument, value_types: Dict[str, Type[AbstractValue]]) -> Iterator[AbstractFact]:
    status = FactStatus(fact.status.value)
    if isinstance(fact.value, dict):
        value = value_types[fact.type_id].from_dict(fact.value)
    elif isinstance(fact.value, Sequence):
        value = tuple(value_types[fact.type_id].from_dict(v) for v in fact.value)
    else:
        raise ValueError
    value = AtomValueFact(
        status=status,
        type_id=fact.type_id,
        value=value,
        id=fact.id
    )
    yield value

    if fact.mention:
        # get only first span of multi-span mention
        node = doc.id2node[fact.mention[0].node_id]
        if not isinstance(node, TextNode):
            return
        mention = TextNodeMention(node, fact.mention[0].start, fact.mention[0].end)
    elif fact.metadata and hasattr(fact.metadata, 'text'):
        # create node
        text = ' '.join(fact.metadata.text)
        mention = TextNodeMention(TextNode(text), 0, len(text))
    else:
        return

    yield MentionFact(
        status=status,
        mention=mention,
        value=value
    )


def convert_relation_fact(fact: RelationFactModel, old2new: Dict[str, AbstractFact]) -> RelationFact:
    status = FactStatus(fact.status.value)
    source = old2new[fact.value.from_fact]
    target = old2new[fact.value.to_fact]
    if not isinstance(source, ConceptFact) or not isinstance(target, ConceptFact):
        raise ValueError
    return RelationFact(
        status=status,
        type_id=fact.type_id,
        source=source,
        target=target,
        id=fact.id
    )


def convert_property_fact(fact: PropertyFactModel, old2new: Dict[str, AbstractFact]) -> Union[PropertyFact, RelationPropertyFact]:
    status = FactStatus(fact.status.value)
    source = old2new[fact.value.from_fact]
    target = old2new[fact.value.to_fact]
    if not isinstance(target, AtomValueFact):
        raise ValueError
    if isinstance(source, ConceptFact):
        return PropertyFact(
            status=status,
            type_id=fact.type_id,
            source=source,
            target=target,
            id=fact.id
        )
    elif isinstance(source, RelationFact):
        return RelationPropertyFact(
            status=status,
            type_id=fact.type_id,
            source=source,
            target=target,
            id=fact.id
        )
    raise ValueError
