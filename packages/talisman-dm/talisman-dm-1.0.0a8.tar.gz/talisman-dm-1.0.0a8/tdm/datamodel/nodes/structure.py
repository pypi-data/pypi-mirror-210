from dataclasses import dataclass
from typing import Optional

from tdm.abstract.datamodel import AbstractNode, BaseNodeMetadata
from tdm.abstract.json_schema import generate_model


@dataclass(frozen=True)
class ListNodeMetadata(BaseNodeMetadata):
    bullet: Optional[str] = None


@generate_model(label='list')
@dataclass(frozen=True)
class ListNode(AbstractNode[ListNodeMetadata]):
    pass


@generate_model(label='json')
@dataclass(frozen=True)
class JSONNode(AbstractNode[BaseNodeMetadata]):
    pass


@generate_model(label='table')
@dataclass(frozen=True)
class TableNode(AbstractNode[BaseNodeMetadata]):
    pass


@dataclass(frozen=True)
class TableRowNodeMetadata(BaseNodeMetadata):
    header: Optional[bool] = None


@generate_model(label='row')
@dataclass(frozen=True)
class TableRowNode(AbstractNode[TableRowNodeMetadata]):
    pass


@dataclass(frozen=True)
class TableCellNodeMetadata(BaseNodeMetadata):
    colspan: Optional[int] = None
    rowspan: Optional[int] = None


@generate_model(label='cell')
@dataclass(frozen=True)
class TableCellNode(AbstractNode[TableCellNodeMetadata]):
    pass
