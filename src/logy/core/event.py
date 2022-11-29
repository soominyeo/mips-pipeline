from abc import ABC, abstractmethod
from enum import Enum
from typing import Generic, TypeVar, Type, Callable, Optional, Union
import json

from logy.core.component import Transceiver, D, E, Element

EV = TypeVar('EV', bound='Event')


class Event(Generic[E], ABC):
    def __init__(self, source: E = None, target: E = None, time: int = None):
        self.source = source
        self.target = target
        self.time = time

    def __init_subclass__(cls, type: str = None, **kwargs):
        super(Event, cls).__init_subclass__(kwargs)
        cls.type = type or cls.__name__

class TransmitEvent(Generic[D], Event[Transceiver[D]]):
    def __init__(self, source: Transceiver[D], target: Transceiver[D], data: D, time: int):
        super(TransmitEvent, self).__init__(source, target, time)
        self.data = data

class InternalEvent(Generic[E], Event[E]):
    pass


class EventHandler(Generic[EV], ABC):
    @abstractmethod
    def matches(self, event: EV) -> bool: ...

    @abstractmethod
    def handle(self, event: EV): ...

    @staticmethod
    def simple(source: Optional[E], event_type: Union[Type[EV], str], handler: Callable[[EV], None]):
        handler = EventHandler.SimpleEventHandler(source, event_type, handler)
        return handler

    class SimpleEventHandler(Generic[EV], 'EventHandler'[EV]):
        def __init__(self, source: Optional[E], event_type: Union[Type[EV], str], handler: Callable[[EV], None]):
            self.__source = source
            self.__event_type = event_type
            self.__handler = handler

        def matches(self, event: EV) -> bool:
            type_matches = (isinstance(self.__event_type, type) and isinstance(event, self.__event_type)) or self.__event_type == event.type
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

    def attach(self, element: Element, handler: EventHandler):
        pass

    def detach(self, element: Element, handler: Union[EventHandler, Callable[[EventHandler], bool], None]):
        if isinstance(handler, EventHandler):
            pass
        elif callable(handler):
            pass
        else:
            pass
