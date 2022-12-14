from __future__ import annotations

import random
import string
from abc import ABC
from copy import copy
from typing import TypeVar, Dict, Collection, Union, Tuple, Generic

from logy.core.helpers import demangled
from logy.core.primitive.data import D, Data

B = TypeVar("B", bound='ElementBehavior')


class ElementBehavior(ABC):
    pass


E = TypeVar("E", bound='Element')


class Element(Generic[B]):
    """
    A base class for all circuit elements.
    Each primitive has name and unique id, with some convenience like prefix, random naming.
    """
    RAND_NAME_SIZE = 5
    entry: Dict[str, Element] = {}

    def __init__(self, name: str = None):
        if not name:
            name = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(Element.RAND_NAME_SIZE))
        self.__name = name
        Element.entry[self.id] = self

    def __init_subclass__(cls, classifier: str = None, states: Collection[Union[Tuple[str, str], str]] = None,
                          **kwargs):
        """
        :param classifier: an inherited name prefix for the class
        :param states: states each primitive should keep and track
        :param behavior: behaviors how each class should operate
        :param kwargs:
        :return:
        """
        super().__init_subclass__(**kwargs)
        # name classifier
        classifier_derived = next(
            (clz.classifier for clz in cls.mro() if clz is not cls and hasattr(clz, 'classifier')), '')
        cls.classifier = classifier_derived + classifier if classifier_derived and classifier else (
                    classifier_derived or classifier or '')
        # primitive state
        cls.states: Dict[str, str] = {alias: name for it in
                                      (clz.states.items() for clz in cls.mro() if hasattr(clz, 'states')) for
                                      alias, name in it}
        if states:
            for state in states:
                state, alias = (state if isinstance(state, tuple) else (state, None))
                cls.add_state(state, alias=alias)

    @classmethod
    def add_state(cls, state, alias: str = None):
        state = demangled(cls, state)
        if (alias or state) in cls.states:
            raise NameError(f"{cls.__name__}: state '{alias}' already defined in the superclass")
        cls.states[alias or state] = state

    def behavior(self) -> B:
        return None

    @property
    def name(self) -> str:
        return self.__name

    @property
    def full_name(self):
        return self.classifier + '_' + self.name if self.classifier else self.name

    @property
    def id(self) -> str:
        return self.__name + '__' + str(id(self))

    @staticmethod
    def find(id: str):
        return Element.entry[id]

    def __del__(self):
        del Element.entry[self.id]

    def __getstate__(self):
        return {alias: copy(self.__dict__.get(name)) for alias, name in self.states.items()}

    def __setstate__(self, state):
        for alias, value in state:
            if alias in self.states.keys():
                self.__setattr__(self.states[alias], value)

    def __setattr__(self, key, value):
        if key in self.states.values() and hasattr(self, key):
            state = self.__getstate__()
            super(Element, self).__setattr__(key, value)
            self.update(state)
        else:
            super(Element, self).__setattr__(key, value)

    def __hash__(self):
        return hash(self.id)

    def update(self, state):
        """
        Handle state changes.
        :param state: previous state before update
        """

    def __repr__(self):
        return f"<<{self.full_name}>>({', '.join(f'{key}: {value}' for key, value in self.__getstate__().items())})"


class BufferedElement(Generic[B, D], Element[B], states=[('__data', 'data')]):
    def __init__(self, data: D, name: str = None):
        super().__init__(name=name)
        self.__data = data

    @property
    def data(self):
        return self.__data

    @data.setter
    def data(self, value: Union[int, D]):
        if isinstance(value, Data):
            if not self.__data.compatible(value):
                raise AttributeError
            self.__data = self.__data.of(value.value)
        else:
            if not self.__data.valid(value):
                raise AttributeError
            self.__data = self.__data.of(value)

    @data.deleter
    def data(self):
        self.__data = self.__data.of(None)


if __name__ == "__main__":
    class MyElement(Element, states=[('value', 'val')]):
        def __init__(self):
            super(MyElement, self).__init__(name='MyElement')
            self.value = 1

        def update(self, state):
            print(self, state)


    element = MyElement()
    element.value = 3
    element.value = 2
