from dataclasses import dataclass
from typing import Optional, Tuple

from immutabledict import immutabledict

from tdm.abstract.datamodel import AbstractDirective, Identifiable
from tdm.abstract.json_schema import generate_model


@dataclass(frozen=True)
class _CreateConceptDirective(AbstractDirective):
    name: str
    concept_type: str
    filters: Tuple[dict, ...]
    notes: Optional[str] = None
    markers: Optional[str] = None
    access_level: Optional[str] = None

    def __post_init__(self):
        filters = tuple(immutabledict(f) for f in self.filters)
        object.__setattr__(self, 'filters', filters)


@generate_model(label='create_concept')
@dataclass(frozen=True)
class CreateConceptDirective(Identifiable, _CreateConceptDirective):
    pass
