from dataclasses import dataclass
from typing import Union

from tdm.abstract.datamodel import AbstractLinkDomainType, Identifiable
from ._composite import CompositeValueType
from ._concept import ConceptType
from ._relation import RelationType
from ._value import AtomValueType

ValueType = Union[CompositeValueType, AtomValueType]


@dataclass(frozen=True)
class PropertyType(Identifiable, AbstractLinkDomainType[ConceptType, ValueType]):
    pass


@dataclass(frozen=True)
class RelationPropertyType(Identifiable, AbstractLinkDomainType[RelationType, ValueType]):
    pass
