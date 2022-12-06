from abc import abstractmethod, ABC
import dataclasses
from functools import reduce
from typing import TypeVar, Generic, Iterable, SupportsIndex, SupportsBytes, Literal, Union, List, Optional

D = TypeVar("D", bound='Data')
D1 = TypeVar("D1", bound='Data')
D2 = TypeVar("D2", bound='Data')

BD = TypeVar('BD', bound='BinaryData')


@dataclasses.dataclass(frozen=True, eq=False)
class Data(Generic[D], ABC):
    value: int

    @abstractmethod
    def valid(self, value: int) -> bool:
        """Check if a value is valid for data."""
        ...

    def __eq__(self, other: D):
        return self.value == other.value

    def __lt__(self, other: D):
        return self.value < other.value

    def compatible(self, other: D):
        """
        Check if two data is compatible.
        """
        return True

    def of(self, value: Optional[int]):
        """
        Get a new data object with new value.
        """
        if not self.valid(value):
            raise AttributeError
        return dataclasses.replace(self, value=value)

    @classmethod
    def reduce(cls, *datas: D) -> D:
        """
        Reduce multiple datas into a single data object
        """
        if len(datas) < 1:
            raise AttributeError
        if not reduce(lambda d, r: r and datas[0].compatible(d), datas[1:], True):
            raise NotImplementedError
        value = reduce(lambda d, r: d.value or r.value, datas[1:], datas[0])
        return datas[0].of(value)


@dataclasses.dataclass(frozen=True, eq=False)
class BinaryData(Generic[BD], Data[BD]):
    length: int
    signed: bool = False

    def valid(self, value: int) -> bool:
        return 0 <= self._to_binary(value, length=self.length, signed=self.signed) < 2 ** self.length

    def compatible(self, other: BD):
        return super().compatible(other) \
               and self.length == other.length and self.signed == other.signed

    def of(self, value: Optional[int], _slice: slice = None):
        if _slice:
            start, stop, _ = _slice.indices(self.length)
            mask = sum(1 << i for i in range(start, stop))
            _slice.indices(self.length)
            return super().of((self.value & ~mask) | ((value << start) & mask))
        return super().of(value)

    def __getitem__(self, item):
        if isinstance(item, slice):
            start, stop, _ = item.indices(self.length)
            mask = sum(1 << i for i in range(start, stop))
            return (self.value & mask) >> start
        else:
            if item < 0 or item >= self.length:
                raise IndexError
            return (self.value >> item) & 1

    @property
    def actual(self):
        return self._to_actual(self.value, length=self.length, signed=self.signed)

    @classmethod
    def _to_binary(cls, actual: int, *, length: int, signed=False):
        return 2 ** length - actual if signed else actual

    @classmethod
    def _to_actual(cls, binary: int, *, length: int, signed=False):
        return 2 ** length - binary if signed else binary
