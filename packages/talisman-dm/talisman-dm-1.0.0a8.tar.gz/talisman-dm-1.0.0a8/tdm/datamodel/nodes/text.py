from dataclasses import dataclass
from typing import Optional

from tdm.abstract.datamodel import AbstractContentNode, BaseNodeMetadata
from tdm.abstract.json_schema import generate_model


@dataclass(frozen=True)
class TextNodeMetadata(BaseNodeMetadata):
    language: Optional[str] = None
    header: bool = False
    header_level: Optional[int] = None

    def __post_init__(self):
        if self.header_level is not None:
            if self.header_level < 0:
                raise ValueError(f"header_level could not be negative (actual: {self.header_level})")
            if not self.header:
                raise ValueError(f"header_level could be specified only with header flag")


@generate_model(label='text')
@dataclass(frozen=True)
class TextNode(AbstractContentNode[TextNodeMetadata, str]):
    pass


@generate_model(label='key')
@dataclass(frozen=True)
class KeyNode(AbstractContentNode[TextNodeMetadata, str]):
    pass
