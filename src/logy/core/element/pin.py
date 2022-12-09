from abc import ABC, abstractmethod
from typing import Generic, Optional, Set, Dict

from logy.core.data import D, Direction
from .component import Component
from .element import Element
from .wire import Wire


class Pin(Generic[D], Element, ABC, classifier="P"):

    def __init__(self, data: D, mode: Direction, name: Optional[str] = None):
        super(Pin, self).__init__(data, name=name)
        self.__wires: Set[Wire[D]] = set()
        self.__mode = mode
        self.__comps: Dict[Component, Direction] = dict()

    @property
    def wires(self):
        return list(self.__wires)

    @property
    def mode(self):
        return self.__mode

    @property
    def comps(self):
        return dict(self.__comps)

    def attach(self, wire: 'Wire[D]'):
        """Attach an incoming/outgoing data wire."""
        self.__wires.add(wire)

    def detach(self, wire: 'Wire[D]', mode: Direction):
        """Detach an incoming/outgoing data wire if attached."""
        if wire in self.__wires:
            self.__wires.remove(wire)

    def mount(self, comp: Component, mode: Direction):
        """
        Mount to a specific element with a specific mode.
        Pin sends an alert to the input-mode mounted element on data input.

        :param comp:
        :param mode: a direction, whether the pin works as an input/output pin.
        """
        self.__comps[comp] = mode

    def dismount(self, comp: Component):
        """
        Dismount from a specific element.
        """
        if comp in self.__comps.keys():
            del self.__comps[comp]

    def update(self, state, actor: Optional[Element] = None):
        super(Pin, self).update(state)

    @abstractmethod
    def alert(self, comp: Component):
        """
        Send an alert to the component.
        """
        ...
