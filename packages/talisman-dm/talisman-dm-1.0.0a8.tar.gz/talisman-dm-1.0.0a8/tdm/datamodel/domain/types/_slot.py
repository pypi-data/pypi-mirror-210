from dataclasses import dataclass

from tdm.abstract.datamodel import AbstractLinkDomainType, Identifiable
from ._composite import CompositeValueType
from ._value import AtomValueType


@dataclass(frozen=True)
class SlotType(Identifiable, AbstractLinkDomainType[CompositeValueType, AtomValueType]):
    pass
