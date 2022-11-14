from typing import *

from .error import DesignError
from .component import *


class CircuitDesigner:
    def __init__(self):
        self.__comp = None
        self.__pin = None

    @property
    def comp(self) -> 'ElementAccess[Component]':
        if self.__comp is None:
            self.__comp = ElementAccess()
        return self.__comp

    @property
    def pin(self) -> 'ElementAccess[Pin]':
        if self.__pin is None:
            self.__pin = ElementAccess()
        return self.__pin


# class ElementAccess(Generic[E]):
#     def __init__(self, parent: Optional['ElementAccess'], name: Optional[str]):
#         self.__parent = parent
#         self.__name = name
#         self.__elements: Dict[str, Union[E, ElementAccess[E]]] = {}
#         self.__map: Dict[str, Tuple[int, int]] = {}
#
#     def __call__(self, offset: int, size: int):
#         self.__offset = offset
#         self.__size = size
#         if self.__parent:
#             if any(True for i in range(offset, offset + size) if self.__parent.__find_nested(i) is not None):
#                 raise DesignError
#             self.__parent[]
#
#     def __find_nested(self, key: int):
#         return next((k for k, (s, e) in self.__map if key in range(s, e)), None)
#
#     def __getattr__(self, key: str) -> Union[E, 'ElementAccess[E]']:
#         if key.startswith('_'):
#             return super(ElementAccess, self).__getattr__(key)
#         if key not in self.__elements.keys():
#             self.__setattr__(key, ElementAccess(self, key))
#         return self.__elements.get(key)
#
#     def __setattr__(self, key: str, value: Union[E, 'ElementAccess[E]', Tuple[int, Union[E, 'ElementAccess[E]']]]):
#         if key.startswith('_'):
#             super(ElementAccess, self).__setattr__(key, value)
#             return
#         if isinstance(value, tuple):
#             index, element = value
#             self.__elements[key] = element
#             self.__setitem__(index, element)
#         else:
#             self.__elements[key] = value
#
#     def __delattr__(self, key: str):
#         if key.startswith('_'):
#             super(ElementAccess, self).__delattr__(key)
#             return
#         del self.__elements[key]
#
#     def __getitem__(self, key: Union[int, slice]) -> Union[List[E], E, None]:
#         if isinstance(key, slice):
#             return [index for index, value in self.__map.keys() if key.start <= index < key.start + key.stop]
#         else:
#             return self.__map[key]
#
#     def __setitem__(self, key: Union[int, slice], value: Union[List[E], E]):
#         if isinstance(key, slice):
#             self.__map = [value[i] if key.start <= i < key.start else self.__map[i]
#                           for i in range(self.__slice.stop)
#                           if key.start <= i < key.start + key.stop or i in self.__map.keys()]
#         else:
#             self.__map[key] = value
#
#     def __delitem__(self, key: int):
#         self.__map[key] = None

class ElementAccess(Generic[E]):
    def __init__(self):
        self.__element: Dict[str, Union[E, ElementAccess[E]]] = {}
        self.__map: Dict[str, Tuple[int, int]] = {}
        self.__space: Dict[int, Union[E]]


    def __getitem__(self, item):
        if isinstance(item, slice):
            nested = self.__find_nested()
            item = [ for i, e in ((i, self.__find_nested(i)) for i in range(item.start, item.stop))]
            for i in range(item.start, item.stop):
                nested = self.__find_nested(i)
                if
                nested[i - self.__map[nested]]


    def __find_nested(self, key: int):
        return next((k for k, (s, e) in self.__map if key in range(s, e)), None)

designer = CircuitDesigner()
designer.pin.write_pin = designer.pin[0:1] = Pin()
designer.pin.read_pin = designer.pin[1:2] = Pin()
