import dataclasses
from collections import defaultdict
from dataclasses import fields
from typing import Any, Dict, Generic, List, Optional, Sequence, Type, TypeVar, Union

from pydantic import BaseModel, Extra, create_model, root_validator
from typing_extensions import Literal, Self

from tdm.helper import cache_result, generics_mapping, register_in_module, unfold_union, uniform_collection
from .serializers import AbstractElementModel, AbstractElementSerializer, BaseSerializers

_Element = TypeVar('_Element')


# hackish root validator solution as normal validators are not called for skipped required fields
def set_type_if_none(cls, values):
    if 'type' not in values:
        values['type'] = cls.__fields__['type'].type_.__args__[0]  # get arg of Literal ('type' field type)
    return values


class ElementModel(BaseModel, AbstractElementModel[_Element], Generic[_Element]):
    class Config:
        extra = Extra.forbid

    def deserialize(self, typed_id2element: Dict[type, Dict[str, Any]]) -> _Element:
        raise NotImplementedError

    @classmethod
    def serialize(cls, element: _Element) -> Self:
        kwargs = {}
        for key, value in element.__dict__.items():
            if value is None or isinstance(value, (str, int, float, dict)):
                kwargs[key] = value
                continue
            elif isinstance(value, Sequence):
                _serialize = lambda s, value=value: type(value)(s.serialize(v) for v in value)
                value_types = {type(v) for v in value}
            else:
                _serialize = lambda s, value=value: s.serialize(value)
                value_types = {type(value)}
            for type_, serializer in BaseSerializers.items():
                if all(issubclass(vt, type_) for vt in value_types):
                    kwargs[key] = _serialize(serializer)
                    break
            else:
                kwargs[key] = value
        return cls(**kwargs)


def _wrap_deserializer(coll_type: type, serializer: AbstractElementSerializer):
    def deserialize(values, *args):
        return coll_type(serializer.deserialize(v, *args) for v in values)

    return deserialize


_BaseType = TypeVar('_BaseType', bound=type)


@cache_result()
def create_model_for_type(type_: Type[_Element], label: Optional[str] = None) -> Type[ElementModel[_Element]]:
    type_vars = generics_mapping(type_)

    model_fields = {}
    validators = {}

    special_fields: Dict[str, List[AbstractElementSerializer]] = defaultdict(list)

    for field in fields(type_):
        name = field.name
        default_value = field.default if field.default is not dataclasses.MISSING else ...
        field_type = type_vars.get(field.type, field.type)
        union_types = unfold_union(field_type)
        model_field = False
        f_t = []
        for t in map(lambda ut: type_vars.get(ut, ut), union_types):
            typing_type, real_type, arg = uniform_collection(t)
            if real_type is type:
                serializer = BaseSerializers[type]
                f_t.append(serializer.field_type(arg))
                special_fields[name].append(serializer.deserialize)
                model_field = True
                continue
            for _type, serializer in BaseSerializers.items():
                if issubclass(arg, _type):
                    if typing_type is None:
                        f_t.append(serializer.field_type(arg))
                        special_fields[name].append(serializer.deserialize)
                    else:
                        f_t.append(typing_type[serializer.field_type(arg)])
                        special_fields[name].append(_wrap_deserializer(real_type, serializer))
                    model_field = True
                    break
            else:
                f_t.append(t)
        if model_field:
            field_type = Union[tuple(f_t)]

        model_fields[name] = (field_type, default_value)
    if label:
        model_fields['type'] = (Literal[label], ...)
        validators['set_if_none'] = root_validator(pre=True, allow_reuse=True)(set_type_if_none)

    model = register_in_module(create_model(f"{type_.__name__}Model", __base__=ElementModel, __validators__=validators, **model_fields))

    def deserialize(self: model, typed_id2element: Dict[type, Dict[str, Any]]) -> type_:
        kwargs = {}
        for f in set(type_.__dataclass_fields__).intersection(self.__dict__):
            kwargs[f] = getattr(self, f)
            if f in special_fields:
                for deserializer in special_fields[f]:
                    try:
                        kwargs[f] = deserializer(kwargs[f], typed_id2element)
                        break
                    except Exception:
                        pass
        return type_(**kwargs)

    model.deserialize = deserialize

    return model
