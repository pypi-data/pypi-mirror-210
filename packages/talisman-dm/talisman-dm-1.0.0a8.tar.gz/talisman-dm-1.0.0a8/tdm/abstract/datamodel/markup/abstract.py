from abc import abstractmethod
from typing import Type, TypeVar

from immutabledict import immutabledict

_AbstractMarkup = TypeVar('_AbstractMarkup', bound='AbstractMarkup')


class AbstractMarkup(object):
    @property
    @abstractmethod
    def markup(self) -> immutabledict:
        pass

    @classmethod
    @abstractmethod
    def from_markup(cls: Type[_AbstractMarkup], markup: 'AbstractMarkup') -> _AbstractMarkup:
        pass

    def __hash__(self):
        return hash(self.markup)

    def __eq__(self, other):
        if not isinstance(other, AbstractMarkup):
            return NotImplemented
        return self.markup == other.markup
