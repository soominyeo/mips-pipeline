from __future__ import annotations

import dataclasses
from abc import ABC, abstractmethod
from typing import Generic, Union, Callable

from logy.core.primitive.data import D, Mode
from logy.core.primitive.element import BufferedElement, ElementBehavior, Element


class PinBehavior(ElementBehavior, ABC):
    """
    A base class for singleton which is responsible for pins' concrete behavior.
    """

    @abstractmethod
    def on_data_update(self, pin: Pin, prev_state):
        """
        Handle the pin's buffered data update.
        """
        ...


class Pin(Generic[D], BufferedElement[PinBehavior, D], classifier="P"):

    def update(self, state):
        super().update(state)
        if state['data'] != self.data:
            self.on_data_update({"data": state['data']})

    def write(self, data: Union[D, int], writer: Element = None):
        self.data = data

    """ methods delegated by behavior """

    def on_data_update(self, prev_state):
        if not self.behavior:
            raise NotImplementedError
        self.behavior().on_data_update(self, prev_state)


@dataclasses.dataclass
class PinEntry:
    pin: Pin
    mode: Mode

    def __hash__(self):
        return hash((self.pin, self.mode))

