__all__ = [
    'Domain', 'DomainManager',
    'set_default_domain', 'get_default_domain',
    'AtomValueType', 'CompositeValueType', 'ConceptType', 'PropertyType', 'RelationPropertyType', 'RelationType', 'SlotType'
]

from typing import Callable, Optional

from ._impl import Domain
from ._manager import DomainManager
from .types import AtomValueType, CompositeValueType, ConceptType, PropertyType, RelationPropertyType, RelationType, SlotType

DEFAULT_DOMAIN_MANAGER = DomainManager()

set_default_domain: Callable[[Optional[Domain]], None] = DEFAULT_DOMAIN_MANAGER.set
get_default_domain: Callable[[], Domain] = DEFAULT_DOMAIN_MANAGER.get
