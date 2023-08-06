from dataclasses import dataclass
from typing import Optional

from tdm.abstract.datamodel import AbstractContentNode, BaseNodeMetadata
from tdm.abstract.json_schema import generate_model


@dataclass(frozen=True)
class FileNodeMetadata(BaseNodeMetadata):
    name: Optional[str] = None
    size: Optional[int] = None


@generate_model(label='file')
@dataclass(frozen=True)
class FileNode(AbstractContentNode[FileNodeMetadata, str]):
    pass


@dataclass(frozen=True)
class ImageNodeMetadata(FileNodeMetadata):
    width: Optional[int] = None
    height: Optional[int] = None


@generate_model(label='image')
@dataclass(frozen=True)
class ImageNode(AbstractContentNode[ImageNodeMetadata, str]):
    pass
