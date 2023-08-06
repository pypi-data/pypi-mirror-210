from dataclasses import dataclass

from immutabledict import immutabledict

from ._helper import freeze_dict
from .abstract import AbstractMarkup


@dataclass(frozen=True)
class FrozenMarkup(AbstractMarkup):
    _markup: immutabledict = immutabledict()

    @property
    def markup(self) -> immutabledict:
        return self._markup

    @classmethod
    def from_markup(cls, markup: AbstractMarkup) -> 'FrozenMarkup':
        if isinstance(markup, FrozenMarkup):
            return markup
        return cls(markup.markup)

    def __hash__(self):
        return hash(self._markup)

    @classmethod
    def freeze(cls, markup: dict) -> 'FrozenMarkup':
        if not isinstance(markup, dict):
            raise ValueError
        return cls(freeze_dict(markup))
