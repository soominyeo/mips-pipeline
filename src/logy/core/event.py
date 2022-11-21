from abc import ABC, abstractmethod
from enum import Enum
from typing import Generic, TypeVar, Type, Callable, Optional, Union

from logy.core.component import Transmitter, D, E, Element

EV = TypeVar('EV', bound='Event')


class Event(Generic[E]):
    def __init__(self, source: E, target: E, time: int):
        self.source = source
        self.target = target
        self.time = time


class TransferEvent(Generic[D], Event[Transmitter[D]]):
    def __init__(self, source: Transmitter[D], target: Transmitter[D], data: D, time: int):
        super(TransferEvent, self).__init__(source, target, time)
        self.data = data

class InternalEvent(Generic[E], Event[E]):



class EventResult:
    pass


class EventHandler(Generic[EV], ABC):
    @abstractmethod
    def matches(self, event: EV) -> bool: ...

    @abstractmethod
    def handle(self, event: EV) -> EventResult: ...


class SimpleEventHandler(Generic[EV], EventHandler[EV]):
    def __init__(self, source: Optional[E], event_type: Type[EV], handler: Callable[[EV], EventResult]):
        self.__source = source
        self.__event_type = event_type
        self.__handler = handler

    def matches(self, event: EV) -> bool:
        return isinstance(event, self.__event_type) and (self.__source is None or self.__source is event.source)

    def handle(self, event: EV) -> EventResult:
        assert self.matches(event)
        return self.__handler(event)


class EventSystem(ABC):
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

