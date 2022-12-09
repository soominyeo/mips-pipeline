import random
import string
from abc import abstractmethod
from typing import TypeVar, Dict, Optional, Collection, Union, Tuple, TYPE_CHECKING

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
        return {alias: self.__dict__.get(name) for alias, name in self.states.items()}

    def __setstate__(self, state):
        for alias, value in state:
            if alias in self.states.keys():
                self.__setattr__(self.states[alias], value)

    def __setattr__(self, key, value):
        if hasattr(self, key) and key in self.states.values():
            state = self.__getstate__()
            super(Element, self).__setattr__(key, value)
            self.update(self)
        else:
            super(Element, self).__setattr__(key, value)
        

    def update(self, state):
        """
        Handle state changes.
        :param state: previous state before update
        """
        return

    def __repr__(self):
        return f"<<{self.name}>>({', '.join(f'{key}: {value}' for key, value in self.__getstate__().items())})"


if __name__ == "__main__":
    class MyElement(Element, states=[('value', 'val')]):
        def __init__(self):
            super(MyElement, self).__init__(name='MyElement')
            self.value = 1

        def update(self, state):
            print(self)

    element = MyElement()
    element.value = 3
