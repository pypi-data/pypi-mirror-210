from abc import ABCMeta
from dataclasses import dataclass, replace
from typing import Callable, Set, Union

from tdm.abstract.datamodel import AbstractDomain, AbstractFact, AbstractNode, AbstractNodeMention, Identifiable
from tdm.abstract.json_schema import generate_model
from .value import AtomValueFact


@dataclass(frozen=True)
class _MentionFact(AbstractFact, metaclass=ABCMeta):
    mention: AbstractNodeMention
    value: AtomValueFact

    @classmethod
    def constant_fields(cls) -> Set[str]:
        return {'mention', 'value'}


@generate_model(label='mention')
@dataclass(frozen=True)
class MentionFact(Identifiable, _MentionFact):

    def replace_with_domain(self, domain: AbstractDomain) -> 'MentionFact':
        value = self.value.replace_with_domain(domain)
        if value is self.value:
            return self
        return replace(self, value=value)

    @staticmethod
    def node_filter(node: Union[AbstractNode, str]) -> Callable[['MentionFact'], bool]:
        node_id = node.id if isinstance(node, AbstractNode) else node

        def _filter(fact: MentionFact) -> bool:
            return fact.mention.node_id == node_id

        return _filter

    @staticmethod
    def value_filter(filter_: Callable[[AtomValueFact], bool]) -> Callable[['MentionFact'], bool]:
        def _filter(fact: MentionFact) -> bool:
            return filter_(fact.value)

        return _filter
