from abc import abstractmethod, ABC
from typing import TypeVar, Generic

D = TypeVar("D", bound='Data')
D1 = TypeVar("D1", bound='Data')
D2 = TypeVar("D2", bound='Data')

class Data(Generic[D], int, ABC):
    @classmethod
    @abstractmethod
    def valid(cls, value: int) -> bool:
        """Check if a value is valid for data"""

    @classmethod
    @abstractmethod
    def join(cls, *args: D) -> D:
        """
        Combine multiple values into a single value

        :raise NotImplementedError: if no behavior defined for this data type
        :raise OverflowError: if joined result does not fulfill validity
        """



