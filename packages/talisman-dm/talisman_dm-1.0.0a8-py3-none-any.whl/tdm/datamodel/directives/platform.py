from dataclasses import dataclass, field

from tdm.abstract.datamodel import AbstractDirective, Identifiable
from tdm.abstract.json_schema import generate_model


@dataclass(frozen=True)
class _CreatePlatformDirective(AbstractDirective):
    key: str
    name: str
    platform_type: str
    url: str


@generate_model(label='create_platform')
@dataclass(frozen=True)
class CreatePlatformDirective(Identifiable, _CreatePlatformDirective):
    id: str = field(default=None, compare=False)
