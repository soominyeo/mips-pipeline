from __future__ import annotations

import dataclasses
from abc import ABC
from typing import (Generic, TypeVar, Union, Any)

from logy.core.primitive import (Pin, Component, Wire)
from logy.core.primitive.data import D

E1 = TypeVar('E1', bound='Element')
E2 = TypeVar('E2', bound='Element')

EV = TypeVar('EV', bound='Event')


@dataclasses.dataclass
class Event(Generic[E1, E2], ABC):
    source: E1
    target: E2
    time: int

    def __init_subclass__(cls, type: str = None, **kwargs):
        super(Event, cls).__init_subclass__(**kwargs)
        cls.type = type or cls.__name__

    def __gt__(self, other: Event):
        return self.time > other.time


    def __hash__(self):
        return hash((self.source, self.target, self.time))


W = TypeVar('W', Wire, Pin)


@dataclasses.dataclass
class WriteEvent(Generic[E1, W, D], Event[E1, W]):
    data: D

@dataclasses.dataclass
class InternalEvent(Event[Union[Pin, Component], Union[Pin, Component]]):
    prev_state: Any
    pass
