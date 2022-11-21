import string
from abc import abstractmethod, ABC
import random
from typing import *
from functools import reduce

from logy.core.error import NonDeterministicError
from logy.core.event import Event, EventHandler, EventSystem

D = TypeVar("D")
E = TypeVar("E", bound='Element')


class Element:
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


class Transmitter(Generic[D], Element):
    @abstractmethod
    def read(self, actor: Optional[Element] = None) -> D: ...

    @abstractmethod
    def write(self, data: D, actor: Optional[Element] = None): ...

    @abstractmethod
    def erase(self, actor: Optional[Element] = None): ...


P = TypeVar("P", bound='Pin')


class Pin(Generic[D], Transmitter[D], classifier="P"):
    def __init__(self, data: D, name: Optional[str] = None):
        super(Pin, self).__init__(name)
        self.__data: D = data
        self.__wire_input: List[Wire[D, P[D]]] = []
        self.__wire_output: List[Wire[D, P[D]]] = []

    @property
    def data(self):
        if self.__data is None:
            self.__data = self.read(None)
        return self.__data

    @data.setter
    def data(self, value: D):
        self.__data = value
        self.write(None, self.__data)

    @data.deleter
    def data(self):
        self.erase()

    def read(self, actor: Optional[Element] = None) -> D:
        data = reduce(lambda a, b: a & b, (wire.read(self) for wire in self.__wire_input))
        return data

    def write(self, data: D, actor: Optional[Element] = None):
        for wire in self.__wire_output:
            wire.write(self, data)

    def erase(self, actor: Optional[Element] = None):
        for wire in self.__wire_output:
            wire.erase(self)


class Wire(Generic[D], Transmitter[D], classifier="W"):
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
    def simple(cls, start: Pin[D], end: Pin[D], delay: int = 0) -> 'Wire':
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
