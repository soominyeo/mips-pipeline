from __future__ import annotations

import dataclasses
from abc import ABC, abstractmethod
from typing import Generic, Iterable, Tuple, Optional, Dict, Set, TYPE_CHECKING, Union

from logy.core.primitive.data import D1, D2, D, Mode
from logy.core.primitive.element import BufferedElement, ElementBehavior, Element
from logy.core.primitive.pin import Pin, PinEntry


class WireBehavior(ElementBehavior, ABC):
    """
    A base class for singleton which is responsible for wires' concrete behavior.
    """

    @abstractmethod
    def on_pin_write(self, wire: Wire, pin: Pin, data: D):
        """
        Handle associated pin's write.
        """
        ...


class Wire(Generic[D, D1, D2], Element[WireBehavior], classifier="W"):
    def __init__(self, pin_ins: Iterable[Tuple[Pin[D1], int]], pin_outs: Iterable[Tuple[Pin[D2], int]],
                 name: str = None):
        super().__init__(name=name)
        self.__delay: Dict[PinEntry, int] = {PinEntry(pin, mode): delay for pins, mode in
                                             [(pin_ins, Mode.IN), (pin_outs, Mode.OUT)] for pin, delay in
                                             pins}
        self.__pins: Set[PinEntry] = set(self.__delay.keys())

    @property
    def pins(self):
        return {entry.pin for entry in self.__pins}

    def get_delay(self, pin: Pin, mode: Mode):
        entry = PinEntry(pin, mode)
        return self.__delay[entry]

    @property
    def entries(self):
        return self.__pins.copy()

    def write(self, data: Union[D1, int], writer: Element = None):
        if not writer or not isinstance(writer, Pin):
            raise NotImplementedError
        self.on_pin_write(writer, data)

    @classmethod
    def direct(cls, start: Pin[D], end: Pin[D], delay: int = 0, name: str = None):
        wire = SimpleWire([(start, delay)], [(end, 0)],
                          name=(name or f"[{start.full_name}:{end.full_name}]"))
        return wire

    @classmethod
    def branch(cls, start: Pin[D], ends: Iterable[Tuple[Pin[D], int]], name: str = None):
        wire = SimpleWire([(start, 0)], [(pin, delay) for pin, delay in ends],
                          name=(name or f"[{start.full_name}:{next(pin.full_name for pin, _ in ends)}...]"))
        return wire

    """ methods delegated by behavior """

    def on_pin_write(self, pin: Pin, data: D):
        self.behavior().on_pin_write(self, pin, data)



class SimpleWire(Generic[D], Wire[D, D, D], ABC, classifier="s"):
    def __init__(self, pin_ins: Iterable[Tuple[Pin[D1], int]], pin_outs: Iterable[Tuple[Pin[D2], int]],
                 name: Optional[str] = None):
        super(SimpleWire, self).__init__(pin_ins, pin_outs, name=name)


# class MultiWire(Generic[BD], Wire[BD, BinaryData, BinaryData], ABC, classifier="m"):
#     def __init__(self, data: D, pins: Iterable[Tuple['Pin[BD]', Direction, Tuple[int, int], int]]):
#         super().__init__(data, [(pin, mode, delay) for pin, mode, _, delay in pins])
#         self.__bitmap: Dict[Wire.PinEntry, Tuple[int, int]] = {Wire.PinEntry(pin, mode): bit for pin, mode, bit, _ in pins}


if __name__ == '__main__':
    from logy.core.primitive.pin import Pin, PinBehavior
    from logy.core.primitive.data import Data

    wires = []


    class MyPinBehavior(PinBehavior):

        def on_data_update(self, pin: Pin, prev_state):
            print(f'data-update {pin.name}: {prev_state["data"]} -> {pin.data}')
            for w in wires:
                if PinEntry(pin, Mode.IN) in w.entries:
                    w.on_pin_write(pin, prev_state)


    class MyWireBehavior(WireBehavior):

        def on_pin_update(self, wire: Wire, pin: Pin, prev_state):
            print(f'pin-update {pin.name} in {wire.name}')


    Pin.behavior = MyPinBehavior()
    Wire.behavior = MyWireBehavior()

    pin1 = Pin(Data(0, default=0), name="1")
    pin2 = Pin(Data(1, default=0), name="2")
    print(pin1, pin2)
    wire = SimpleWire.direct(pin1, pin2, name="wire")
    wires.append(wire)
    print(wire)
    pin1.write(1)
