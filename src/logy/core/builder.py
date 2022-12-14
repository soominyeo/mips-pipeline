from __future__ import annotations
from typing import Set, Dict, Callable, List, Union

from logy.core.primitive import PinEntry, Component, Wire, Mode, Pin
from logy.core.system import InternalEvent, EventHandler


class ComponentBuilder:
    def __init__(self):
        self.__name: str = None
        self.__pins: Set[PinEntry] = set()
        self.__pin_names: Dict[str, PinEntry] = {}
        self.__wires: Set[Wire] = set()
        self.__comps: Set[Component] = set()
        self.__comp_names: Dict[str, Component] = {}
        self.__handlers: List[EventHandler[InternalEvent]] = []

    def name(self, name: str) -> ComponentBuilder:
        self.__name = name
        return self

    def pin(self, pin: Pin, mode: Mode, id: str = None) -> ComponentBuilder:
        entry = PinEntry(pin, mode)
        self.__pins.add(entry)
        if id:
            self.__pin_names[id] = entry
        return self

    def wire(self, wire: Wire) -> ComponentBuilder:
        self.__wires.add(wire)
        return self

    def comp(self, comp: Component, id: str = None) -> ComponentBuilder:
        self.__comps.add(comp)
        if id:
            self.__comp_names[id] = comp
        return self

    def handler(self, handler: EventHandler[Union[InternalEvent[Pin, Component], InternalEvent[Component, Pin]]]):
        self.__handlers.append(handler)
        return self

    def build(self) -> Component:
        comp = ComponentBuilder.BuiltComponent(self.__name, self.__pins, self.__pin_names, self.__wires, self.__comps, self.__comp_names)
        return comp
        pass

    class BuiltComponent(Component):
        def __init__(self, name: str, pins: Set[PinEntry], pin_names: Dict[str, PinEntry], wires: Set[Wire],
                     comps: Set[Component],
                     comp_names: Dict[str, Component]
                     ):
            super().__init__(
                [(entry.pin, entry.mode, next((name for name, e in pin_names if e == entry), None)) for entry in pins],
                wires, comps, name=name)
            self.__wires = set(wires)
            self.__comp_names = comp_names.copy()


