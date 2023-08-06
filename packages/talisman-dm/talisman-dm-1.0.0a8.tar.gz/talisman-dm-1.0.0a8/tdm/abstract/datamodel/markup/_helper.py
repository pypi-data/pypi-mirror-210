from typing import Mapping, Sequence

from immutabledict import immutabledict


def freeze_dict(obj: Mapping) -> immutabledict:
    return immutabledict((k, freeze(v)) for k, v in obj.items())


def freeze(obj):
    if obj is None or isinstance(obj, (str, int, float, bool)):
        return obj
    if isinstance(obj, Mapping):
        return freeze_dict(obj)
    if isinstance(obj, set):
        return frozenset(freeze(v) for v in obj)
    if isinstance(obj, Sequence):
        return tuple(freeze(v) for v in obj)
    raise ValueError
