from __future__ import annotations

from queue import PriorityQueue
from typing import Set, Callable, Union, Tuple, List

from logy.core.primitive import PinBehavior, WireBehavior, ComponentBehavior, Pin, Wire, Component, PinEntry, Mode
from logy.core.system import InternalEvent, EventHandler, Event, WriteEvent, \
    EventHandlerImpl, EventSystem
from logy.core.system.handler import handler


class Logy:

    def __init__(self):
        self.__pins: Set[Pin] = set()
        self.__wires: Set[Wire] = set()
        self.__comps: Set[Component] = set()
        self.__pin_behavior = Logy.PinBehavior(self)
        self.__wire_behavior = Logy.WireBehavior(self)
        self.__component_behavior = Logy.ComponentBehavior(self)
        Pin.behavior = lambda pin: self.__pin_behavior
        Wire.behavior = lambda wire: self.__wire_behavior
        Component.behavior = lambda comp: self.__component_behavior

        self.system = Logy.EventSystem()
        self.system.attach(Logy.write_handler)
        self.system.attach(Logy.pin_to_state_sync_handler)
        self.system.attach(Logy.state_to_pin_sync_handler)

    @staticmethod
    @handler(WriteEvent)
    def write_handler(event: WriteEvent):
        event.target.write(event.data, event.source)

    @staticmethod
    @handler(InternalEvent, sources=[Pin], targets=[Component])
    def pin_to_state_sync_handler(event: InternalEvent):
        event.target.on_pin_update(event.source, event.prev_state)

    @staticmethod
    @handler(InternalEvent, sources=[Component], targets=[Pin])
    def state_to_pin_sync_handler(event: InternalEvent):
        data = next(event.source.__getattribute__(alias) for id, alias in event.source.pin_mapped.items() if (entry := event.source.get_pin(id)).pin is event.target and entry.mode is Mode.OUT)
        event.source.write_pin(event.target, data)


    @property
    def pins(self):
        return set(self.__pins)

    @property
    def wires(self):
        return set(self.__wires)

    @property
    def comps(self):
        return set(self.__comps)

    def add_pin(self, *pins: Pin):
        for pin in pins:
            self.__pins.add(pin)

    def add_wire(self, *wires: Wire):
        for wire in wires:
            self.__wires.add(wire)

    def add_comp(self, *comps: Component):
        for comp in comps:
            self.__comps.add(comp)
            self.add_comp(*comp.comps)
            self.add_wire(*comp.wires)
            self.add_pin(*comp.pins)

    class EventSystem(EventSystem):
        MAX_SIZE: int = 1024

        def __init__(self):
            self.__time = 0
            self.__handlers: List[EventHandler] = []
            self.__queue: PriorityQueue[Event] = PriorityQueue(maxsize=Logy.EventSystem.MAX_SIZE)

        @property
        def queue(self):
            return list(self.__queue.queue)

        def peek_queue(self):
            return self.__queue.queue[0]

        def now(self) -> int:
            return self.__time

        def advance(self, time_diff: int):
            while not self.__queue.empty():
                if self.peek_queue().time > self.__time + time_diff:
                    break
                event = self.__queue.get()
                self.execute(event)
            self.__time += time_diff

        def schedule(self, event: Event):
            self.__queue.put(event)

        def execute(self, event: Event):
            for handler in self.__handlers:
                if handler.matches(event):
                    handler.handle(event)
            print(f"executed {event}")

        def attach(self, handler: EventHandler):
            self.__handlers.append(handler)

        def detach(self, handler: Union[EventHandler, Callable[[EventHandler], bool], None]):
            if isinstance(handler, EventHandler):
                self.__handlers.remove(handler)
            elif callable(handler):
                for h in list(self.__handlers):
                    if handler(h):
                        self.__handlers.remove(h)
            else:
                raise AttributeError

    class BaseBehavior:
        def __init__(self, logy: Logy):
            self.__logy = logy

        @property
        def system(self):
            return self.logy.system

        @property
        def logy(self):
            return self.__logy

    class PinBehavior(PinBehavior, BaseBehavior):
        def on_data_update(self, pin: Pin, prev_state):
            for wire in self.logy.wires:
                if PinEntry(pin, Mode.IN) in wire.entries:
                    self.system.schedule(
                        WriteEvent(pin, wire, self.system.after(wire.get_delay(pin, Mode.IN)), pin.data))
            for comp in self.logy.comps:
                if PinEntry(pin, Mode.IN) in comp.entries:
                    self.system.schedule(
                        InternalEvent(pin, comp, self.system.after(comp.get_delay(pin, Mode.IN)), prev_state))

    class WireBehavior(WireBehavior, BaseBehavior):

        def on_pin_write(self, wire: Wire, pin: Pin, data):
            for entry in wire.entries:
                if entry.mode is Mode.OUT:
                    self.system.schedule(
                        WriteEvent(wire, entry.pin, self.system.after(wire.get_delay(entry.pin, Mode.OUT)), data))

    class ComponentBehavior(ComponentBehavior, BaseBehavior):

        def on_pin_update(self, comp: Component, pin: Pin, prev_state):
            for id, alias in list(comp.pin_mapped.items()):
                if comp.get_pin(id).pin is pin:
                    comp.__setattr__(alias, pin.data)

        def on_comp_update(self, comp: Component, subcomp: Component, prev_state):
            return

        def on_state_update(self, comp: Component, state, prev_state):
            updated_states = [name for name, value in state.items() if value != prev_state[name]]
            for updated in updated_states:
                # state affects another state
                affected = comp.pin_affected.get(updated, set())
                for aff_name in affected:
                    comp.__getattribute__(aff_name)

                # state affects output pin
                entry = next((comp.get_pin(id) for id, name in comp.pin_mapped.items() if name == updated), None)
                if entry and entry.mode is Mode.OUT:
                    self.system.schedule(
                        InternalEvent(comp, entry.pin, self.system.after(comp.get_delay(entry.pin, entry.mode)), prev_state))

        def write_pin(self, comp: Component, pin: Pin[D], data: D):
            pin.write(data, comp)


if __name__ == '__main__':
    from logy.builtin.register import Register
    from logy.core.primitive.data import BinaryData, D

    logy = Logy()

    reg1 = Register(BinaryData(0, length=8), name="1")
    reg2 = Register(BinaryData(0, length=8), name="2")

    logy.add_comp(reg1, reg2)

    logy.add_pin(pin_clk := Pin(BinaryData(0, length=1), name="GCLK"))
    logy.add_wire(wire_direct := Wire.direct(reg1.pin_data_out, reg2.pin_data_in),
                  wire_branch := Wire.branch(pin_clk, [(reg1.pin_clk, 0), (reg2.pin_clk, 0)])
                  )

    print(logy.pins, logy.wires)
    logy.system.schedule(WriteEvent(None, reg1.pin_data_in, 0, 255))
    logy.system.schedule(WriteEvent(None, pin_clk, 5, 1))
    logy.system.schedule(WriteEvent(None, pin_clk, 7, 0))
    logy.system.schedule(WriteEvent(None, reg1.pin_data_in, 10, 133))
    logy.system.schedule(WriteEvent(None, pin_clk, 15, 1))
    logy.system.schedule(WriteEvent(None, pin_clk, 17, 0))

    logy.system.advance(14)

    print(reg1, reg2)
