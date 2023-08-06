import importlib
from typing import Any, Dict, Generic, Type, TypeVar

from tdm.abstract.json_schema.serializers import AbstractElementSerializer
from tdm.abstract.json_schema.serializers.abstract import _Element

_ARG = TypeVar('_ARG')


class TypeSerializer(AbstractElementSerializer[Type[_ARG], str], Generic[_ARG]):
    def serialize(self, element: Type[_ARG]) -> str:
        module = element.__module__
        if module == 'builtins':
            return element.__qualname__
        return f"{module}.{element.__qualname__}"

    def deserialize(self, serialized: str, typed_id2element: Dict[type, Dict[str, Any]]) -> Type[_ARG]:
        if '.' not in serialized:
            import builtins
            return getattr(builtins, serialized)
        module_name, name = serialized.rsplit('.', 1)
        module = importlib.import_module(module_name)
        return getattr(module, name)

    def field_type(self, element_type: Type[_Element]) -> Type[str]:
        return str
