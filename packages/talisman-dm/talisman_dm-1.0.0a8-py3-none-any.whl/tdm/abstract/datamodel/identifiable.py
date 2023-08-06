import uuid
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass, field
from typing import Set


@dataclass(frozen=True)
class EnsureIdentifiable(object):  # we need such ugly inheritance to guarantee default valued fields follows fields without defaults

    def __post_init__(self):
        if not isinstance(self, Identifiable):
            raise TypeError(f"{type(self)} should inherit {Identifiable}. Actual mro is {type(self).mro()}")

    @classmethod
    @abstractmethod
    def constant_fields(cls) -> Set[str]:
        pass


@dataclass(frozen=True)
class Identifiable(EnsureIdentifiable, metaclass=ABCMeta):
    id: str = field(default_factory=lambda: None)

    def __post_init__(self):
        if self.id is None:
            object.__setattr__(self, 'id', self.generate_id())
        for type_ in type(self).mro():
            if issubclass(type_, Identifiable):
                continue
            if hasattr(type_, '__post_init__'):
                type_.__post_init__(self)

    @staticmethod
    def generate_id() -> str:
        return str(uuid.uuid4())
