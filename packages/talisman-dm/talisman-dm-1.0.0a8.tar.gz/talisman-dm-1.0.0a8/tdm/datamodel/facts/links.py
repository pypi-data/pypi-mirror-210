from dataclasses import dataclass
from typing import Union

from tdm.abstract.datamodel import AbstractLinkFact, Identifiable
from tdm.abstract.json_schema import generate_model
from tdm.datamodel.domain import PropertyType, RelationPropertyType, RelationType, SlotType
from .concept import ConceptFact
from .value import AtomValueFact, CompositeValueFact


@generate_model(label='relation')
@dataclass(frozen=True, eq=False)
class RelationFact(Identifiable, AbstractLinkFact[ConceptFact, ConceptFact, RelationType]):
    pass


ValueFact = Union[AtomValueFact, CompositeValueFact]


@generate_model(label='property')
@dataclass(frozen=True, eq=False)
class PropertyFact(Identifiable, AbstractLinkFact[ConceptFact, ValueFact, PropertyType]):
    pass


@generate_model(label='r_property')
@dataclass(frozen=True, eq=False)
class RelationPropertyFact(Identifiable, AbstractLinkFact[RelationFact, ValueFact, RelationPropertyType]):
    pass


@generate_model(label='slot')
@dataclass(frozen=True, eq=False)
class SlotFact(Identifiable, AbstractLinkFact[CompositeValueFact, ValueFact, SlotType]):
    pass
