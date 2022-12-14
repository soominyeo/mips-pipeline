from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, Collection, Union, Type, Callable, Iterable

from logy.core.primitive import Element
from logy.core.system.event import EV, E1, E2


class EventHandler(Generic[EV], Callable[[EV], None], ABC):
    def __call__(self, event: EV):
        if self.matches(event):
            self.handle(event)

    @abstractmethod
    def matches(self, event: EV) -> bool: ...

    @abstractmethod
    def handle(self, event: EV): ...

    @staticmethod
    def simple(source: Union[E1, None, Type[E1]], target: Union[E2, None, Type[E2]],
               event_types: Collection[Union[Type[EV], str]],
               eventhandler: Callable[[EV], None],
               matcher: Callable[[EV], bool] = None):
        eventhandler = EventHandlerImpl(source, target, event_types, matcher, eventhandler)
        return eventhandler


class EventHandlerImpl(Generic[EV], EventHandler[EV]):
    def __init__(self, event_types: Collection[Union[Type[EV], str]],
                 sources: Iterable[Union[E1, None, Type[E1]]],
                 targets: Iterable[Union[E2, None, Type[E2]]],
                 matcher: Callable[[EV], bool], handler: Callable[[EV], None]):
        self.__sources = sources
        self.__targets = targets
        self.__event_types = event_types
        self.__matcher = matcher
        self.__handler = handler

    def matches(self, event: EV) -> bool:
        type_matches = any(isinstance(event, t) if isinstance(t, type)
                           else t == event.type for t in self.__event_types)
        source_matches = self.match_element(event.source, self.__sources)
        target_matches = self.match_element(event.target, self.__targets)
        matcher_matches = self.__matcher(event) if self.__matcher else True
        return type_matches and source_matches and target_matches and matcher_matches

    @staticmethod
    def match_element(element: Element, etypes):
        # etype is...
        # None: no restriction
        # Type(Element): type restricted
        # otherwise: instance restricted
        return not etypes or not any(not (etype is None or (
            isinstance(element, etype) if isinstance(etype, type) else
            element is etype)) for etype in etypes)

    def handle(self, event: EV):
        # assert self.matches(event)
        self.__handler(event)


def handler(*event_types: Union[Type[EV], str], sources: Iterable[Union[E1, None, Type[E1]]] = None,
            targets: Iterable[Union[E2, None, Type[E2]]] = None,
            matcher: Callable[[EV], bool] = None):
    def decorator(func: Callable[[EV], None]) -> EventHandler:
        return EventHandlerImpl(event_types, sources, targets, matcher, func)

    return decorator
