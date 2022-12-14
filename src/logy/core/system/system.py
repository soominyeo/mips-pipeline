from __future__ import annotations

from abc import ABC, abstractmethod
from ctypes import Union
from typing import Callable

from logy.core.primitive import Element
from logy.core.system.event import Event
from logy.core.system.handler import EventHandler


class EventSystem(ABC):
    @abstractmethod
    def now(self) -> int:
        """
        Get current time of the eventsystem.
        """
        ...

    def after(self, time_diff: int):
        """
        Get time after given time from the current time
        """
        return self.now() + time_diff

    @abstractmethod
    def advance(self, time_diff: int):
        """
        Advance current time by specific amount of time.
        """

    @abstractmethod
    def schedule(self, event: Event):
        """
        Schedule an event.
        """
        ...

    @abstractmethod
    def execute(self, event: Event):
        """
        Execute an event, mostly handling the event.
        """
        ...

    @abstractmethod
    def attach(self, handler: EventHandler):
        """
        Attach a handler to the eventsystem.
        """
        ...

    @abstractmethod
    def detach(self, handler: Union[EventHandler, Callable[[EventHandler], bool], None]):
        """
        Detach a handler from the eventsystem.

        detach(handler)
        detach(predicate)
        """
        ...
