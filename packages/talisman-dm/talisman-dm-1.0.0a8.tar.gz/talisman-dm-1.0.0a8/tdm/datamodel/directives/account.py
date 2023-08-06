from dataclasses import dataclass

from tdm.abstract.datamodel import AbstractDirective, Identifiable
from tdm.abstract.json_schema import generate_model


@dataclass(frozen=True)
class _CreateAccountDirective(AbstractDirective):
    key: str
    platform_key: str
    name: str
    url: str


@generate_model(label='create_account')
@dataclass(frozen=True)
class CreateAccountDirective(Identifiable, _CreateAccountDirective):
    pass
