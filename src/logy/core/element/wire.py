from abc import ABC
from typing import Generic, Iterable, Tuple, Optional, Dict, Collection

from logy.core.data import D1, D2, D, Direction
from logy.core.element.element import Element
from logy.core.element.pin import Pin


class Wire(Generic[D1, D2], Element, ABC, classifier="W"):
    pass


class SimpleWire(Generic[D], Wire[D], ABC, classifier="W"):
    def __init__(self, pin_inputs: Iterable[Tuple[Pin[D], int]], pin_outputs: Iterable[Tuple[Pin[D], int]],
                 name: Optional[str] = None):
        super(Wire, self).__init__(name)
        self._pin_inputs: Dict[Pin[D], int] = {pin: delay for pin, delay in pin_inputs}
        self._pin_outputs: Dict[Pin[D], int] = {pin: delay for pin, delay in pin_outputs}

    @classmethod
    def direct(cls, start: Pin[D], end: Pin[D], delay: int = 0):
        wire = SimpleWire([(start, delay)], [(end, 0)], name=f"{start.name}>>{end.name}")
        return wire

    @classmethod
    def branch(cls, start: Pin[D], end: Iterable[Tuple[Pin[D], int]]):
        wire = SimpleWire([(start, 0)], end)
        return wire

    def attach(self):
        for pin in self._pin_inputs.keys():
            pin.attach(self, Direction.OUT)
        for pin in self._pin_outputs.keys():
            pin.attach(self, Direction.IN)

    def detach(self):
        for pin in self._pin_inputs.keys():
            pin.detach(self, Direction.OUT)
        for pin in self._pin_outputs.keys():
            pin.detach(self, Direction.IN)
