from dataclasses import dataclass

from tdm.abstract.datamodel import AbstractDomainType, Identifiable


@dataclass(frozen=True)
class ConceptType(Identifiable, AbstractDomainType):
    pass
