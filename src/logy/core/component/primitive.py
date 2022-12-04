import string
from abc import abstractmethod, ABC
import random
from typing import TypeVar, Dict, Optional, Collection, Union, Tuple, Generic, Iterable, List, TYPE_CHECKING

from logy.core.component.data import D, D1, D2
from logy.core.component.transfer import Receivable, Transmittable

if TYPE_CHECKING:
    from logy.core.event import EventSystem
E = TypeVar("E", bound='Element')


class Element:
    """
    A base class for all circuit elements.
    Each element has name and unique id, with some convenience like prefix, random naming.
    """
    RAND_NAME_SIZE = 5
    entry: Dict[str, 'Element'] = {}

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

    @property
    @abstractmethod
    def eventsystem(self) -> 'EventSystem':
        ...

    def __repr__(self):
        return f"<<{self.name}>>)"


class Receiver(Generic[D], Receivable[D], Element, ABC, states=[('__inbound', 'inbound')]):
    """A base class for elements capable of receiving data."""

    def __init__(self, name: Optional[str] = None):
        super(Receiver, self).__init__(name=name)
        self.__inbound: Dict['Transmittable[D]', D] = {}

    @property
    @abstractmethod
    def sources(self) -> Collection['Transmitter[D]']:
        """Get sources, or transmitters writing to the receiver."""
        ...

    def _get_inbound(self, source: 'Transmittable[D]') -> Optional[D]:
        return self.__inbound[source]

    def _set_inbound(self, source: 'Transmittable[D]', value: Optional[D]):
        self.__inbound[source] = value

    def _del_inbound(self, source: 'Transmittable[D]'):
        del self.__inbound[source]


class Transmitter(Generic[D], Transmittable[D], Element, ABC, states=[('__outbound', 'outbound')]):
    """A base class for elements capable of sending data."""

    def __init__(self, name: Optional[str] = None):
        super(Transmitter, self).__init__(name=name)
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

    def _get_outbound(self, dest: 'Receivable[D]') -> Optional[D]:
        return self.__outbound[dest]

    def _set_outbound(self, dest: 'Receivable[D]', value: Optional[D]):
        self.__outbound[dest] = value

    def _del_outbound(self, dest: 'Receivable[D]'):
        del self.__outbound[dest]


class Transceiver(Generic[D1, D2], Receiver[D1], Transmitter[D2], ABC):
    pass


class PassiveTransceiver(Generic[D1, D2], Transceiver[D1, D2], ABC):
    def update(self, state, actor: Optional[Element] = None):
        super(PassiveTransceiver, self).update(state, actor)
        if state['inbound'][actor] != self.__getstate__()['inbound'][actor]:
            self.eventsystem.schedule(TransmitBeginEvent)


class DataHolder(Generic[D], Element, ABC, states=[('data', '__data')]):
    """A base class which can store data as a state."""

    def __init__(self, default: Optional[D]):
        super(DataHolder, self).__init__()
        self._default = default
        self.__data = default

    @property
    def data(self):
        return self.__data

    @data.setter
    def data(self, value: D):
        self.__data = value

    @data.deleter
    def data(self):
        self.__data = self._default


P = TypeVar("P", bound='Pin')


class Pin(Generic[D], Transceiver[D, D], classifier="P"):
    @property
    def sources(self) -> Collection['Transmitter[D]']:
        return list(self._wire_input)

    @property
    def destinations(self) -> Collection['Receiver[D]']:
        return list(self._wire_output)

    def __init__(self, default_data: D = None, name: Optional[str] = None):
        super(Pin, self).__init__(name)
        self._default_data = default_data
        self._data_map: Dict[Optional[E], Optional[D]] = {}
        self._wire_input: List[Wire[D]] = []
        self._wire_output: List[Wire[D]] = []


class Wire(Generic[D], Receiver[D], Transmitter[D], classifier="W"):
    def __init__(self, read_pins: Iterable[Tuple[Pin[D], int]], write_pins: Iterable[Tuple[Pin[D], int]],
                 name: Optional[str] = None):
        super(Wire, self).__init__(name)
        self.__read_pins: Dict[Pin[D], int] = {pin: delay for pin, delay in read_pins}
        self.__write_pins: Dict[Pin[D], int] = {pin: delay for pin, delay in write_pins}

    def read(self, actor: Optional[Pin] = None) -> D:
        pass

    def write(self, data: D, actor: Optional[Pin[D]] = None):
        pass

    def erase(self, actor: Optional[Pin[D]] = None):
        pass

    @classmethod
    def direct(cls, start: Pin[D], end: Pin[D], delay: int = 0) -> 'Wire':
        wire = Wire([(start, delay)], [(end, 0)], name=f"{start.name}>>{end.name}")
        return wire

    @classmethod
    def branch(cls, start: Pin[D], end: Iterable[Tuple[Pin[D], int]]) -> 'Wire':
        wire = Wire([(start, 0)], end)
        return wire


class Component(Element, classifier="C"):
    def __init__(self, pins: Tuple[Iterable[Pin], Iterable[Pin]] = ((), ()), components: Iterable['Component'] = (),
                 name: Optional[str] = None):
        super(Component, self).__init__(name)
        self.__pin_inputs: List[P] = list(pins[0])
        self.__pin_outputs: List[P] = list(pins[1])
        self.__comps = list(components)

    @property
    def pin_inputs(self):
        return list(self.__pin_inputs)

    @property
    def pin_outputs(self):
        return list(self.__pin_outputs)

    @property
    def comps(self):
        return list(self.__comps)
