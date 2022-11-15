import string
from abc import abstractmethod, ABC
import random
from typing import *
from functools import reduce

from logy.core.error import NonDeterministicError

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

    def update(self):
        pass

    @property
    def name(self) -> str:
        return self.__name

    @property
    def id(self) -> str:
        return self.__name + '__' + str(id(self))

    def __repr__(self):
        return f"<<{self.name}>>)"


class Transferable(Generic[D], ABC):
    @abstractmethod
    def read(self) -> D: ...

    @abstractmethod
    def write(self, data: D): ...

    @abstractmethod
    def erase(self): ...


P = TypeVar("P", bound='Pin')


class Pin(Generic[D], Transferable[D], Element[D], classifier="P"):
    def __init__(self, data: D, name: Optional[str] = None):
        super(Pin, self).__init__(name)
        self.__data: D = data
        self.__wire_input: List[Wire[D, P[D]]] = []
        self.__wire_output: List[Wire[D, P[D]]] = []

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

    def read(self) -> D:
        data = reduce(lambda a, b: a & b, (wire.read(self) for wire in self.__wire_input))
        return data

    def write(self, data: D):
        for wire in self.__wire_output:
            wire.write(self, data)

    def erase(self):
        for wire in self.__wire_output:
            wire.erase(self)


class Wire(Generic[D, P], Element, classifier="W"):
    def __init__(self, start: P, end: P, name: Optional[str] = None):
        super(Wire, self).__init__(name or start.name + '>>' + end.name)

    @abstractmethod
    def read(self, pin: P): ...

    @abstractmethod
    def write(self, pin: P, data: D): ...

    @abstractmethod
    def erase(self, pin: P): ...


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
