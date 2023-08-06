from typing import Type

from tdm.abstract.datamodel import AbstractNodeLink
from tdm.abstract.json_schema import AbstractLabeledModel, get_model_generator


def register_node_link_models() -> Type[AbstractLabeledModel[AbstractNodeLink]]:
    import tdm.datamodel.links as links
    links

    return get_model_generator(AbstractNodeLink).generate_labeled_model('NodeLinksModel')


NodeLinksModel = register_node_link_models()
