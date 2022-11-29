import itertools
import functools
import string
from abc import abstractmethod, ABC
import random
from typing import *

from logy.core.error import NonDeterministicError
from logy.core.event import Event, TransmitEvent, EventHandler, EventSystem

D = TypeVar("D")
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

    def __init_subclass__(cls, classifier: Optional[str] = None, **kwargs):
        super().__init_subclass__(**kwargs)
        derived = next((clz.classifier for clz in cls.mro() if hasattr(clz, 'classifier')), '')
        cls.classifier = derived + '_' + classifier if derived and classifier else (derived or classifier or '')

    def __del__(self):
        del Element.entry[self.id]

    @staticmethod
    def find(id: str):
        return Element.entry[id]

    @abstractmethod
    @property
    def eventsystem(self) -> EventSystem: ...

    @property
    def name(self) -> str:
        return self.__name

    @property
    def id(self) -> str:
        return self.__name + '__' + str(id(self))

    def __repr__(self):
        return f"<<{self.name}>>)"


class Transceiver(Generic[D], Element):
    """
    A base class for elements which are capable of sending and receiving data.
    """

    @abstractmethod
    @property
    def candidates(self) -> Collection['Transceiver[D]']:
        """
        Get candidates of the writer transceivers.
        :return: a collection of the transceivers.
        """

    @abstractmethod
    def read(self, actor: Optional['Transceiver'] = None) -> D:
        """
        Read data from the transceiver.
        :param actor: the element trying to read data
        :return: read data
        """

    @abstractmethod
    def write(self, data: D, actor: Optional['Transceiver'] = None):
        """
        Write data to the transceiver.
        :param data: data to write
        :param actor: the element trying to write data
        """

    @abstractmethod
    def erase(self, actor: Optional[Element] = None):
        """
        Erase data from the transceiver.
        :param actor: the element trying to erase data
        """

    @abstractmethod
    def update(self, data, actor: Optional[Element] = None):
        """
        Update data and handle changes.
        :param data: data to update
        :param actor: the element which invoked update at the first time
        """


class PassiveTransceiver(Generic[D], Transceiver[D], ABC):
    """
    A class for transceivers that automatically spread data changes.
    """

    @abstractmethod
    @property
    def destinations(self) -> Transceiver[D]:
        """

        :return:
        """


P = TypeVar("P", bound='Pin')


class Pin(Generic[D], Transceiver[D], classifier="P"):
    def __init__(self, default_data: D = None, name: Optional[str] = None):
        super(Pin, self).__init__(name)
        self._default_data = default_data
        self._data_map: Dict[Optional[E], Optional[D]] = {}
        self._wire_input: List[Wire[D, P[D]]] = []
        self._wire_output: List[Wire[D, P[D]]] = []

    @property
    def data(self):
        return self.read()

    @data.setter
    def data(self, value: D):
        self.write(value)

    @data.deleter
    def data(self):
        self.erase()

    def read(self, actor: Optional[Element] = None) -> D:
        candidates = [data for data, _ in set(self._data_map.values()) if data is not None]
        if len(candidates) > 1:
            raise NonDeterministicError
        return candidates[0] if candidates else self._default_data

    def write(self, data: D, actor: Optional[Element] = None):
        prev = self.read()
        self._data_map[actor] = data
        for wire in self._wire_output:
            self.eventsystem.schedule(TransmitEvent(self, wire, data, 0))

    def erase(self, actor: Optional[Element] = None):
        del self._data_map[actor]
        for wire in self._wire_output:
            wire.erase(self)


class Wire(Generic[D], Transceiver[D], classifier="W"):
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
