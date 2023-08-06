from typing import Any, Dict, Type, Union

from tdm.abstract.datamodel import AbstractDomainType
from tdm.abstract.json_schema.serializers import AbstractElementSerializer
from tdm.abstract.json_schema.serializers.abstract import _Element


class DomainTypeSerializer(AbstractElementSerializer[Union[str, AbstractDomainType], str]):
    def serialize(self, element: Union[str, AbstractDomainType]) -> str:
        return element if isinstance(element, str) else element.id

    def deserialize(self, serialized: str, typed_id2element: Dict[type, Dict[str, Any]]) -> Union[str, AbstractDomainType]:
        return typed_id2element.get(AbstractDomainType, {}).get(serialized, serialized)

    def field_type(self, element_type: Type[_Element]) -> Type[str]:
        return str
