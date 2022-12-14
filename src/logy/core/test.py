from __future__ import annotations

from typing import List, Set

from logy.core.primitive import Wire, Component, PinBehavior, Pin, PinEntry, Mode, WireBehavior, ComponentBehavior, D


class Test:

    def __init__(self):
        self.pins: Set[Pin] = set()
        self.wires: Set[Wire] = set()
        self.comps: Set[Component] = set()
        self.pin_behavior = Test.MyPinBehavior(self)
        self.wire_behavior = Test.MyWireBehavior(self)
        self.component_behavior = Test.MyComponentBehavior(self)
        Pin.behavior = lambda pin: self.pin_behavior
        Wire.behavior = lambda wire: self.wire_behavior
        Component.behavior = lambda comp: self.component_behavior

    def add_pin(self, *pins: Pin):
        for pin in pins:
            self.pins.add(pin)

    def add_wire(self, *wires: Wire):
        for wire in wires:
            self.wires.add(wire)

    def add_comp(self, *comps: Component):
        for comp in comps:
            self.comps.add(comp)
            self.add_comp(*comp.comps)
            self.add_pin(*comp.pins)

    class MyPinBehavior(PinBehavior):
        def __init__(self, test: Test):
            self.test = test

        def on_data_update(self, pin: Pin, prev_state):
            print(f'Pin.on_data_update {pin.name}: {prev_state["data"]} -> {pin.data}')
            for w in self.test.wires:
                if PinEntry(pin, Mode.IN) in w.entries:
                    w.on_pin_write(pin, prev_state)
            for c in self.test.comps:
                if PinEntry(pin, Mode.IN) in c.entries:
                    c.on_pin_update(pin, prev_state)

    class MyWireBehavior(WireBehavior):
        def on_data_update(self, wire: Wire, prev_state):
            pass

        def __init__(self, test: Test):
            self.test = test

        def on_pin_write(self, wire: Wire, pin: Pin, data):
            print(f'Wire.on_pin_update {pin.name} in {wire.name}')
            wire.data = pin.data
            for pin, mode in wire.entries:
                if mode is Mode.IN:
                    pin.write(wire.data)

    class MyComponentBehavior(ComponentBehavior):

        def on_state_update(self, comp: Component, state, prev_state):
            pass

        def __init__(self, test: Test):
            self.test = test

        def on_pin_update(self, comp: Component, pin: Pin, prev_state):
            print(f'Component.on_pin_update {pin.name} in {comp}')
            for id, alias in list(comp.pin_mapped.items()):
                if comp.get_pin(id).pin is pin:
                    comp.__getattribute__(alias)

        def on_comp_update(self, comp: Component, subcomp: Component, prev_state):
            pass

        def write_pin(self, comp: Component, pin: Pin[D], data: D):
            pin.write(data)
