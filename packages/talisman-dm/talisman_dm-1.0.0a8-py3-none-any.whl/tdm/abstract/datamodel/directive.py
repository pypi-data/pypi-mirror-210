from dataclasses import dataclass
from typing import Set

from .identifiable import EnsureIdentifiable


@dataclass(frozen=True)
class AbstractDirective(EnsureIdentifiable):

    @classmethod
    def constant_fields(cls) -> Set[str]:
        return set()
