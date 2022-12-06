from __future__ import annotations
import dataclasses
from abc import ABC, abstractmethod
from typing import (Generic, TypeVar, Type, Callable, Optional, Union, Collection, TYPE_CHECKING)

from logy.core.component import (D, Element, E, Transmitter, Receiver)

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


@dataclasses.dataclass
class TransmitBeginEvent(Generic[D], Event[Transmitter[D], Receiver[D]]):
    data: D


@dataclasses.dataclass
class InternalEvent(Generic[E1, E2], Event[E1, E2]):
    pass


class EventHandler(Generic[EV], ABC):
    @abstractmethod
    def matches(self, event: EV) -> bool: ...

    @abstractmethod
    def handle(self, event: EV): ...

    @staticmethod
    def simple(source: Optional[E], event_types: Collection[Union[Type[EV], str]], handler: Callable[[EV], None]):
        handler = SimpleEventHandler(source, event_types, handler)
        return handler


class SimpleEventHandler(Generic[EV], EventHandler[EV]):
    def __init__(self, source: Optional[E], event_types: Collection[Union[Type[EV], str]],
                 handler: Callable[[EV], None]):
        self.__source = source
        self.__event_types = event_types
        self.__handler = handler

    def matches(self, event: EV) -> bool:
        type_matches = any(isinstance(event, t) if isinstance(t, type)
                           else t == event.type for t in self.__event_types)
        source_matches = type_matches and (self.__source is None or self.__source is event.source)
        return type_matches and source_matches

    def handle(self, event: EV):
        assert self.matches(event)
        self.__handler(event)


class EventSystem(ABC):
    def advance(self, time_diff: int):
        pass

    def schedule(self, event: Event):
        pass

    def trigger(self, event: Event):
        pass

    def attach(self, element: 'Element', handler: EventHandler):
        pass

    def detach(self, element: 'Element', handler: Union[EventHandler, Callable[[EventHandler], bool], None]):
        if isinstance(handler, EventHandler):
            pass
        elif callable(handler):
            pass
        else:
            pass
