import string
from abc import abstractmethod, ABC
import random
from typing import TypeVar, Dict, Optional, Collection, Union, Tuple, Generic, Iterable, List, TYPE_CHECKING, Set, Any

from logy.core.component.data import D, D1, D2, BD, BinaryData
from logy.core.component.transfer import Receivable, Transmittable, Direction

if TYPE_CHECKING:
    from logy.core.event import EventSystem, TransmitBeginEvent, TransmitEndEvent

E = TypeVar("E", bound='Element')


class Element:
    """
    A base class for all circuit elements.
    Each element has name and unique id, with some convenience like prefix, random naming.
    """
    RAND_NAME_SIZE = 5
    entry: Dict[str, 'Element'] = {}
    eventsystem: 'EventSystem' = None

    def __init__(self, name: Optional[str] = None):
        if not name:
            name = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(Element.RAND_NAME_SIZE))
        self.__name = self.classifier + '_' + name
        Element.entry[self.id] = self

    def __init_subclass__(cls, classifier: Optional[str] = None, states: Collection[Union[Tuple[str, str], str]] = None,
                          **kwargs):
        super().__init_subclass__(**kwargs)
        # name classifier
        derived = next((clz.classifier for clz in cls.mro() if hasattr(clz, 'classifier')), '')
        cls.classifier = derived + '_' + classifier if derived and classifier else (derived or classifier or '')
        # element state
        cls.states: Dict[str, str] = {alias: name for it in
                                      (clz.states.items() for clz in cls.mro() if hasattr(clz, 'states')) for
                                      alias, name in it}
        if states:
            for state in states:
                name, alias = (state if isinstance(state, tuple) else (state, None))
                name = name if not name.startswith('__') else '_' + cls.__name__ + name
                if (alias or name) in cls.states:
                    raise NameError(f"{cls.__name__}: state '{alias}' already defined in the superclass")
                cls.states[alias or name] = name

    @property
    def name(self) -> str:
        return self.__name

    @property
    def id(self) -> str:
        return self.__name + '__' + str(id(self))

    @staticmethod
    def find(id: str):
        return Element.entry[id]

    def __del__(self):
        del Element.entry[self.id]

    def __getstate__(self):
        return {alias: self.__dict__.get(name) for alias, name in self.states}

    def __setstate__(self, state):
        for alias, value in state:
            if alias in self.states.keys():
                self.__setattr__(self.states[alias], value)

    @abstractmethod
    def update(self, state, actor: Optional['Element'] = None):
        """
        Handle state changes by other element.
        :param state: previous state before update
        :param actor: the element which invoked update primarily
        """

    def __repr__(self):
        return f"<<{self.name}>>)"

class Receiver(Generic[D], Receivable[D], ABC, states=[('__inbound', 'inbound')]):
    """
    A base class for elements capable of receiving data.
    D1 stands for the data received, while D stands for actual data stored.
    """

    def __init__(self, data: D, name: Optional[str] = None):
        super(Receiver, self).__init__(data, name=name)
        self.__inbound: Dict[Transmittable[D], D] = {}

    @property
    @abstractmethod
    def sources(self) -> Collection['Transmitter[D]']:
        """Get sources, or transmitters writing to the receiver."""
        ...

    def _get_inbound(self, source: Transmittable[D]) -> Optional[D1]:
        return self.__inbound[source]

    def _set_inbound(self, source: Transmittable[D], value: Optional[D1]):
        self.__inbound[source] = value

    def _del_inbound(self, source: Transmittable[D]):
        del self.__inbound[source]


class Transmitter(Generic[D], Transmittable[D], ABC, states=[('__outbound', 'outbound')]):
    """A base class for elements capable of sending data."""

    def __init__(self, data: D, name: Optional[str] = None):
        super(Transmitter, self).__init__(data, name=name)
        self.__outbound: Dict['Receivable[D]', D] = {}

    @property
    @abstractmethod
    def destinations(self) -> Collection['Receiver[D]']:
        """Get destinations, or receivables reading from the transmitter. """
        ...

    @abstractmethod
    def send(self, dest: 'Receiver[D]', data: D):
        """Send data to the destination."""

    @abstractmethod
    def abort(self, dest: 'Receiver[D]'):
        """Abort sending data to the destination"""

    def _get_outbound(self, dest: Receivable[D]) -> Optional[D]:
        return self.__outbound[dest]

    def _set_outbound(self, dest: Receivable[D], value: Optional[D]):
        self.__outbound[dest] = value

    def _del_outbound(self, dest: Receivable[D]):
        del self.__outbound[dest]


class Transceiver(Generic[D1, D2], Receiver[D1], Transmitter[D2], ABC):
    """
    A class which is both a receiver and a transmitter.
    """
    pass


class PassiveTransceiver(Generic[D1, D2], Transceiver[D1, D2], ABC):
    """
    A transceiver which automatically spread inbound updates to outbounds.
    """

    def transform(self, inbound: D1) -> D2:
        """Transform incoming data into outgoing data."""
        return inbound

    def update(self, state, actor: Optional[Element] = None):
        super(PassiveTransceiver, self).update(state, actor)
        if state['inbound'][actor] != (self.inbound[actor]) and state['data'] != self.data:
            outbound = self.transform(self.read(None))
            if outbound.value is None:
                for dest in self.destinations:
                    self.abort(dest)
            else:
                for dest in self.destinations:
                    self.send(dest, outbound)


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


P = TypeVar("P", bound='Pin')


class Pin(Generic[D], PassiveTransceiver[D, D], ABC, classifier="P"):

    def __init__(self, data: D, name: Optional[str] = None):
        super(Pin, self).__init__(data, name=name)
        self._wire_inputs: Set[Wire[D]] = set()
        self._wire_outputs: Set[Wire[D]] = set()
        self._comps: Dict[Component, Direction] = dict()

    @property
    def sources(self) -> Collection['Transmitter[D]']:
        return list(self._wire_inputs)

    @property
    def destinations(self) -> Collection['Receiver[D]']:
        return list(self._wire_outputs)

    def attach(self, wire: 'Wire[D]', mode: Direction):
        """Attach an incoming/outgoing data wire."""
        if mode is Direction.IN:
            self._wire_inputs.add(wire)
        elif mode is Direction.OUT:
            self._wire_outputs.add(wire)

    def detach(self, wire: 'Wire[D]', mode: Direction):
        """Detach an incoming/outgoing data wire if attached."""
        if mode is Direction.IN and wire in self._wire_inputs:
            self._wire_inputs.remove(wire)
        elif mode is Direction.OUT and wire in self._wire_outputs:
            self._wire_outputs.remove(wire)

    def mount(self, comp: Component, mode: Direction):
        """
        Mount to a specific component with a specific mode.
        Pin sends an alert to the input-mode mounted component on data input.

        :param comp:
        :param mode: a direction, whether the pin works as an input/output pin.
        """
        self._comps[comp] = mode

    def dismount(self, comp: Component):
        """
        Dismount from a specific component.
        """
        if comp in self._comps.keys():
            del self._comps[comp]

    def update(self, state, actor: Optional[Element] = None):
        super(Pin, self).update(state, actor)
        if state['data'] != self.data:
            for comp, mode in self._comps:
                if mode is Direction.IN:
                    self.alert(comp)

    @abstractmethod
    def alert(self, comp: Component):
        """
        Send an alert to the component.
        """
        ...


class Wire(Generic[D1, D2], ABC, classifier="W"):


class SimpleWire(Generic[D1, D2], PassiveTransceiver[D1, D2], ABC, classifier="W"):
    def __init__(self, pin_inputs: Iterable[Tuple[Pin[D], int]], pin_outputs: Iterable[Tuple[Pin[D], int]],
                 name: Optional[str] = None):
        super(Wire, self).__init__(name)
        self._pin_inputs: Dict[Pin[D], int] = {pin: delay for pin, delay in pin_inputs}
        self._pin_outputs: Dict[Pin[D], int] = {pin: delay for pin, delay in pin_outputs}

    @property
    def sources(self) -> Collection['Transmitter[D]']:
        return self._pin_inputs

    @property
    def destinations(self) -> Collection['Receiver[D]']:
        return self._pin_outputs

    @classmethod
    def direct(cls, start: Pin[D], end: Pin[D], delay: int = 0):
        wire = Wire([(start, delay)], [(end, 0)], name=f"{start.name}>>{end.name}")
        return wire

    @classmethod
    def branch(cls, start: Pin[D], end: Iterable[Tuple[Pin[D], int]]):
        wire = Wire([(start, 0)], end)
        return wire

    def attach(self):
        for pin in self._pin_inputs.keys():
            pin.attach_out(self)
        for pin in self._pin_outputs.keys():
            pin.attach_in(self)

    def detach(self):
        for pin in self._pin_inputs.keys():
            pin.detach_out(self)
        for pin in self._pin_outputs.keys():
            pin.detach_in(self)
