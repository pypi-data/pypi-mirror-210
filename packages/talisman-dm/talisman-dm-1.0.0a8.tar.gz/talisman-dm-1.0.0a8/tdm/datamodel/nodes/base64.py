from dataclasses import dataclass
from typing import Optional

from tdm.abstract.datamodel import AbstractContentNode, BaseNodeMetadata
from tdm.abstract.json_schema import generate_model


@dataclass(frozen=True)
class Base64NodeMetadata(BaseNodeMetadata):
    content_type: Optional[str] = None


@generate_model(label='base64')
@dataclass(frozen=True)
class Base64Node(AbstractContentNode[Base64NodeMetadata, str]):
    pass
