import string
from abc import abstractmethod, ABC
import random
from typing import *
from functools import reduce

from src.logy.core.error import NonDeterministicError

D = TypeVar("D")
E = TypeVar("E", bound='Element')

class Element(ABC):
    RAND_NAME_SIZE = 15
    entry: Dict[str, 'Element'] = {}

    def __init__(self, name: Optional[str] = None):
        if not name:
            name = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(Element.RAND_NAME_SIZE))
        self.__name = self.prefix + '_' + name
        Element.entry[self.id] = self

    def __init_subclass__(cls, prefix: Optional[str] = None, **kwargs):
        super().__init_subclass__(kwargs)
        cls.prefix = prefix

    def __del__(self):
        del Element.entry[self.id]

    @abstractmethod
    def update(self): ...

    @property
    def name(self) -> str:
        return self.__name

    @property
    def id(self) -> str:
        return self.__name + '_' + str(id(self))


class Transferable(Generic[D], Element, ABC):
    @abstractmethod
    def read(self) -> D: ...

    @abstractmethod
    def write(self, data: D): ...

    @abstractmethod
    def erase(self): ...


P = TypeVar("P", bound='Pin')

class IPin(Generic[D], Transferable[D], ABC, prefix="P"):
    def __init__(self, name: Optional[str] = None):
        super(IPin, self).__init__(name)
        self.__data: Optional[D] = None

    @property
    def data(self):
        if self.__data is None:
            self.__data = self.read()
        return self.__data

    @data.setter
    def data(self, value: D):
        self.__data = value
        self.write(self.__data)

    @data.deleter
    def data(self):
        self.erase()

class Pin(Generic[D], IPin[D]):
    def __init__(self, name: Optional[str] = None):
        super(Pin, self).__init__(name)
        self.__wire_input: List[Wire[D, P[D]]] = []
        self.__wire_output: List[Wire[D, P[D]]] = []

    def read(self) -> D:
        data = reduce(lambda a, b: a & b, (wire.read(self) for wire in self.__wire_input))
        return data

    def write(self, data: D):
        for wire in self.__wire_output:
            wire.write(self, data)

    def erase(self):
        for wire in self.__wire_output
            wire.erase(self)


class Wire(Generic[D, P], Element, prefix="W"):
    def __init__(self, start: P, end: P, name: Optional[str] = None):
        super(Wire, self).__init__(name or start.name + '>>' + end.name)

    @abstractmethod
    def read(self, pin: P): ...

    @abstractmethod
    def write(self, pin: P, data: D): ...

    @abstractmethod
    def erase(self, pin: P): ...

C = TypeVar("C", bound='Component')


class Component(Element, prefix="C"):
    def __init__(self, *components: 'Component', name: Optional[str] = None):
        super(Component, self).__init__(name)
        self.__pin_input: List[P] = []
        self.__pin_output: List[P] = []


class ComponentProxy(Generic[C]):