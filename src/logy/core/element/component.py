from typing import Iterable, Optional, Set

from .element import Element
from .primitive import Pin
from logy.core.data import Direction


class Component(Element, classifier="C"):

    def __init__(self, pin_inputs: Iterable['Pin'] = (), pin_outputs: Iterable['Pin'] = (),
                 components: Iterable['Component'] = (),
                 name: Optional[str] = None):
        super(Component, self).__init__(name)
        self._pin_inputs: Set[Pin] = set()
        self._pin_outputs: Set[Pin] = set()
        self.__comps = list(components)
        for pin in pin_inputs:
            self.attach(pin, Direction.IN)
        for pin in pin_outputs:
            self.attach(pin, Direction.OUT)

    def attach(self, pin: 'Pin[D]', mode: Direction):
        if mode is Direction.IN:
            self._pin_inputs.add(pin)
        elif mode is Direction.OUT:
            self._pin_outputs.add(pin)

    def detach(self, pin: 'Pin[D]', mode: Direction):
        if mode is Direction.IN and pin in self._pin_inputs:
            self._pin_inputs.remove(pin)
        elif mode is Direction.OUT and pin in self._pin_outputs:
            self._pin_outputs.remove(pin)

    @property
    def pin_inputs(self):
        return list(self._pin_inputs)

    @property
    def pin_outputs(self):
        return list(self._pin_outputs)

    @property
    def comps(self):
        return list(self.__comps)
