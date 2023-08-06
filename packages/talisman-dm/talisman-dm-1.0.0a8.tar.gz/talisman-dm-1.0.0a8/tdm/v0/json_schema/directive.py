from enum import Enum
from typing import Optional, Tuple, Union

from pydantic import BaseModel
from typing_extensions import Literal


class DirectiveType(str, Enum):
    CREATE_CONCEPT = 'create_concept'
    CREATE_ACCOUNT = 'create_account'
    CREATE_PLATFORM = 'create_platform'


class AbstractDirectiveModel(BaseModel):
    directive_type: DirectiveType


class CreateConceptDirectiveModel(AbstractDirectiveModel):
    id: str
    name: str
    concept_type: str
    filters: Tuple[dict, ...]
    notes: Optional[str]
    markers: Optional[Tuple[str, ...]]
    access_level: Optional[str]

    directive_type: Literal[DirectiveType.CREATE_CONCEPT] = DirectiveType.CREATE_CONCEPT

    def __hash__(self):
        return hash((self.directive_type, self.concept_type, self.id))


class CreateAccountDirectiveModel(AbstractDirectiveModel):
    key: str
    platform_key: str
    name: str
    url: str

    directive_type: Literal[DirectiveType.CREATE_ACCOUNT] = DirectiveType.CREATE_ACCOUNT

    def __hash__(self):
        return hash((self.directive_type, self.key))


class CreatePlatformDirectiveModel(AbstractDirectiveModel):
    key: str
    platform_type: str
    name: str
    url: str

    directive_type: Literal[DirectiveType.CREATE_PLATFORM] = DirectiveType.CREATE_PLATFORM

    def __hash__(self):
        return hash((self.directive_type, self.key))


DirectiveModel = Union[CreateAccountDirectiveModel, CreateConceptDirectiveModel, CreatePlatformDirectiveModel]
