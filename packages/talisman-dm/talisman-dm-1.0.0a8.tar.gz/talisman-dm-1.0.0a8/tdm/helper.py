import sys
from typing import Any, Callable, Collection, Dict, Generic, List, Optional, Set, Tuple, TypeVar, Union


def unfold_union(type_: type) -> Tuple[type, ...]:
    # check if it is union
    if hasattr(type_, '__origin__') and type_.__origin__ is Union:
        return type_.__args__
    return type_,


_COLLECTIONS = {
    tuple: List,  # in other case Tuple[A, ...] is converted to Tuple[A]. Deserializes to tuple
    set: Set,
    list: List,
    dict: Dict
}


def map_type(type_: type) -> type:
    return _COLLECTIONS.get(type_, type_)


def uniform_collection(type_: type) -> Tuple[Optional[type], Optional[type], type]:
    if not hasattr(type_, '__origin__'):
        return None, None, type_
    if issubclass(type_.__origin__, Collection):
        args = tuple(filter(lambda t: t is not ..., type_.__args__))
        if len(args) != 1:
            raise NotImplementedError
        return map_type(type_.__origin__), type_.__origin__, args[0]
    if type_.__origin__ is type:
        return None, type, type_.__args__[0]
    raise TypeError


def check_base_type(type_: type, base_type: type) -> bool:
    if issubclass(type_, base_type):  # check simple subclass
        return True
    if not hasattr(type_, '__origin__'):  # check if it is some generic (Union, Tuple, etc)
        return False
    origin = type_.__origin__
    if not issubclass(origin, Tuple):  # check if it is tuple
        return False
    for arg in filter(lambda t: t is not ..., type_.__args__):  # check each argument except Ellipsis
        if not issubclass(arg, base_type):  # Now we assume only Tuple[type_, ...]
            return False
    return True


def is_subclass(type_: type, base_type: type) -> bool:
    try:
        return all(check_base_type(t, base_type) for t in unfold_union(type_))
    except TypeError:
        return False


def cache_result(key_param: Optional[str] = None, cache: Optional[dict] = None):
    if cache is None:
        cache = {}

    def wrap(f: Callable):
        def wrapper(*args, **kwargs) -> Any:
            if key_param is not None:
                key = kwargs[key_param]
            elif args:
                key = args[0]
            else:
                key = kwargs[next(iter(kwargs))]
            if key in cache:
                return cache[key]
            result = f(*args, **kwargs)
            cache[key] = result
            return result

        return wrapper

    return wrap


def generics_mapping(type_: type) -> Dict[TypeVar, type]:
    if issubclass(type_, Generic):  # actually it works (should be rewritten in more pythonic way)
        # assume type vars are not intersect
        result = {}
        for orig_base in type_.__orig_bases__:
            if '__origin__' in orig_base.__dict__ and '__args__' in orig_base.__dict__:
                result.update(dict(zip(orig_base.__origin__.__parameters__, orig_base.__args__)))
        return result
    return {}


_T = TypeVar('_T', bound=type)


def register_in_module(t: _T) -> _T:
    module = t.__module__
    name = t.__name__
    if hasattr(sys.modules[module], name):
        if getattr(sys.modules[module], name) is not t:
            raise RuntimeError
    else:
        setattr(sys.modules[module], name, t)
    return t
