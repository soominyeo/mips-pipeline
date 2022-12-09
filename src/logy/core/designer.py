from typing import *
from itertools import zip_longest

from logy.core.error import DesignError
from logy.core.element import *


class CircuitDesigner:
    def __init__(self):
        self.__comp = None
        self.__pin = None

    @property
    def comp(self) -> 'NamedElementAccess[Component]':
        if self.__comp is None:
            self.__comp = NamedElementAccess()
        return self.__comp

    @property
    def pin(self) -> 'NamedElementAccess[Pin]':
        if self.__pin is None:
            self.__pin = NamedElementAccess()
        return self.__pin

    def connect(self, _from: Pin, _to: Pin):
        pass

    def build(self):
        pass


K = TypeVar('K', str, int)


class ElementAccess(Generic[K, E]):
    def __init__(self):
        self._elements: Dict[K, Union[E, ElementAccess[E]]] = {}

    def __call__(self, size: int):
        self.__class__ = IndexedElementAccess
        self._size = size

    def _repr_sub(self):
        return ''

    def __getitem__(self, key: K):
        if key not in self._elements.keys():
            self.__setitem__(key, ElementAccess())
        return self._elements.get(key)

    def __setitem__(self, key: K, value: Union[Iterable[Union[E, 'ElementAccess[E]']], E, 'ElementAccess[E]']):
        if key in self._elements.keys() and isinstance(element := self._elements.get(key), IndexedElementAccess):
            element[:] = value
        else:
            self._elements[key] = value

    def __delitem__(self, key: K):
        del self._elements[key]

    def __getattr__(self, key: K):
        if self.__class__ == ElementAccess:
            self.__class__ = NamedElementAccess
            return NamedElementAccess.__getattr__(self, key)

    def __repr__(self):
        return f"{'N' if isinstance(self, NamedElementAccess) else ('I' if isinstance(self, IndexedElementAccess) else '')}({self._repr_sub()})"


class NamedElementAccess(Generic[E], ElementAccess[str, E]):
    def _repr_sub(self):
        return ', '.join(f'{k}={e.__repr__()}' for k, e in self._elements.items())

    def __getattr__(self, key: str):
        if key.startswith('_'):
            return super(NamedElementAccess, self).__getattribute__(key)
        return self.__getitem__(key)

    def __setattr__(self, key: str, value: Union[Iterable[Union[E, 'ElementAccess[E]']], E, 'ElementAccess[E]']):
        if key.startswith('_'):
            super(NamedElementAccess, self).__setattr__(key, value)
            return
        return self.__setitem__(key, value)


class IndexedElementAccess(Generic[E], ElementAccess[int, E]):
    def _repr_sub(self):
        return '[' + ', '.join(str(e) for k, e in sorted(self._elements.items(), key=lambda x: x[0])) + ']'

    def __init__(self, size: int):
        super(IndexedElementAccess, self).__init__()
        self._size = size

    def __getitem__(self, key: Union[int, slice]):
        if isinstance(key, slice):
            return [self.__getitem__(i) for i in range(key.start, key.stop)]
        else:
            return super(IndexedElementAccess, self).__getitem__(key)

    def __setitem__(self, key: Union[int, slice],
                    value: Union[Iterable[Union[E, 'ElementAccess[E]']], E, 'ElementAccess[E]']):
        if isinstance(key, slice):
            indices = key.indices(self._size)
            for i, v in zip_longest(range(indices[0], indices[1]), value):
                if i is not None and v is not None:
                    self.__setitem__(i, v)
                elif i is not None and i in self._elements.keys():
                    self.__delitem__(i)
        else:
            return super(IndexedElementAccess, self).__setitem__(key, value)


if __name__ == "__main__":
    designer = CircuitDesigner()
    designer.comp.reg_file = Component()
    designer.comp.buffer(2)
    designer.comp.buffer[:] = [Component(name="buffer_1"), Component(name="buffer_2")]




    print(designer.comp)
    print(Pin())