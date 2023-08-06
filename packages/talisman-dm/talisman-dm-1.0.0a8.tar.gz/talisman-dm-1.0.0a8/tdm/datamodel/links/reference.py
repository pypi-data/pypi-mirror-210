from dataclasses import dataclass
from typing import Callable, Optional

from tdm.abstract.datamodel import AbstractNodeLink, AbstractNodeMention, Identifiable
from tdm.abstract.json_schema import generate_model


@generate_model(label='same')
@dataclass(frozen=True)
class SameNodeLink(Identifiable, AbstractNodeLink[AbstractNodeMention, AbstractNodeMention]):
    pass


@generate_model(label='translation')
@dataclass(frozen=True)
class TranslationNodeLink(Identifiable, AbstractNodeLink[AbstractNodeMention, AbstractNodeMention]):
    language: Optional[str] = None

    @staticmethod
    def lang_filter(language: str) -> Callable[['TranslationNodeLink'], bool]:
        def _filter(link: TranslationNodeLink) -> bool:
            return link.language == language

        return _filter


@generate_model(label='reference')
@dataclass(frozen=True)
class ReferenceNodeLink(Identifiable, AbstractNodeLink[AbstractNodeMention, AbstractNodeMention]):
    pass
