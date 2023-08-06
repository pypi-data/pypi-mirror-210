from tdm.abstract.datamodel import AbstractDomainType, AbstractFact, AbstractMarkup, AbstractNode, AbstractNodeMention, AbstractValue, \
    BaseNodeMetadata
from .domain import DomainTypeSerializer
from .identifiable import IdSerializer
from .markup import MarkupSerializer
from .mention import NodeMentionSerializer
from .metadata import NodeMetadataSerializer
from .type_ import TypeSerializer
from .value import ValueSerializer


def build_serializers():
    result = {
        AbstractNode: IdSerializer(AbstractNode),
        AbstractFact: IdSerializer(AbstractFact),
        AbstractNodeMention: NodeMentionSerializer(),
        BaseNodeMetadata: NodeMetadataSerializer(),
        AbstractValue: ValueSerializer(),
        AbstractMarkup: MarkupSerializer(),
        AbstractDomainType: DomainTypeSerializer(),
        type: TypeSerializer()
    }
    # other serializers could be added here
    return result
