from __future__ import annotations

from abc import abstractmethod, ABC
from typing import Iterable, Set, Dict, Union, List, Any, Callable, Tuple

from logy.core.primitive.data import Mode, D
from logy.core.primitive.element import Element, ElementBehavior
from logy.core.primitive.pin import PinEntry


class ComponentBehavior(ElementBehavior, ABC):
    """
    A base class for singleton which is responsible for components' concrete behavior.
    """

    @abstractmethod
    def on_pin_update(self, comp: Component, pin: Pin, prev_state):
        """
        Handle attached pin's update.
        """
        ...

    @abstractmethod
    def on_comp_update(self, comp: Component, subcomp: Component, prev_state):
        """
        Handle an included component's update.
        """
        ...

    @abstractmethod
    def on_state_update(self, comp: Component, state, prev_state):
        """
        Handle the component's state update.
        """
        ...

    @abstractmethod
    def write_pin(self, comp: Component, pin: Pin[D], data: D):
        """
        Write data to the pin.
        """
        ...


class Component(Element[ComponentBehavior], classifier="C"):
    def __init__(self, pins: Iterable[Union[Tuple[Pin, Mode, str]]] = (),
                 wires: Iterable[Wire] = (),
                 components: Iterable[Component] = (),
                 name: str = None):
        super(Component, self).__init__(name)
        self.__pins: Set[PinEntry] = set()
        self.__pin_names: Dict[str, PinEntry] = {}

        for pin, mode, id in pins:
            entry = PinEntry(pin, mode)
            self.__pins.add(entry)
            if id:
                self.__pin_names[id] = entry

        self.__wires: Set[Wire] = set(wires)
        self.__comps: Set[Component] = set(components)

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # pin_mapped: pin_id -> state_name
        # pin_affect: state_name -> *pin_id
        # pin_delay: pin_id -> delay
        cls.pin_mapped: Dict[str, str] = dict()
        cls.pin_affected: Dict[str, Set[str]] = dict()
        cls.pin_delay: Dict[str, int] = dict()

    @property
    def pins(self):
        return {entry.pin for entry in self.__pins}

    @property
    def wires(self):
        return set(self.__wires)

    @property
    def entries(self):
        return self.__pins.copy()

    @property
    def comps(self):
        return set(self.__comps)

    @classmethod
    def mapped(cls, id: Union[Pin[D], str], mode: Mode, delay: int = 0, srcs: Iterable[Union[str]] = (), eval=None):
        """Define a pin-mapped property by id and mode."""

        def decorator(func: Union[Callable[[Component, Any], D], Callable[[D], Any]]):
            name, state = cls.name_mapped(func.__name__), func.__name__

            if mode is Mode.IN:

                def getter(self):
                    if state not in self.states.keys():
                        self.pin_mapped[id] = state
                        self.pin_delay[id] = delay
                        self.add_state(name, alias=state)
                    if not hasattr(self, name):
                        self.__setattr__(state, self.get_pin(id).pin.data)
                    return self.__getattribute__(name)

                def setter(self, data: D):
                    value = func(self, data)
                    if not hasattr(self, name) or self.__getattribute__(name) != value:
                        self.__setattr__(name, value)

                return property(getter, fset=setter)
            elif mode is Mode.OUT:
                def getter(self):
                    if state not in self.states.keys():
                        self.pin_mapped[id] = state
                        self.pin_delay[id] = delay
                        self.add_state(name, alias=state)
                        for src in srcs:
                            self.pin_affected[src] = self.pin_affected.get(src, set()).union({state})
                    value = eval(*[self.__getattribute__(src) for src in srcs])
                    if not hasattr(self, name) or self.__getattribute__(name) != value:
                        self.__setattr__(name, value)
                    return value

                def setter(self, value):
                    if self.__getattribute__(name) != value:
                        self.__setattr__(name, value)

                return property(getter if eval else None, fset=setter)

        return decorator

    @staticmethod
    def name_mapped(name: str):
        return f"_mapped_{name}"

    def update(self, state):
        super().update(state)
        for name, value in self.__getstate__().items():
            if value != state[name]:
                self.on_state_update({name: state[name]}, {name: value})

    def get_pin(self, id: str):
        return self.__pin_names[id]

    def get_delay(self, pin: Pin, mode: Mode):
        entry = PinEntry(pin, mode)
        if entry in self.__pin_names.values():
            name = next(name for name, e in self.__pin_names.items() if e == entry)
            return self.pin_delay[name]
        return 0

    def attach(self, pin: Pin, mode: Mode, id: Union[int, str] = None):
        entry = PinEntry(pin, mode)
        self.__pins.add(entry)
        if id:
            self.__pin_names[id] = entry

    def detach(self, arg: Union[Pin, Union[int, str]], mode: Mode = None):
        if isinstance(arg, int) or isinstance(arg, str):
            entry = self.get_pin(arg)
            self.__pins.remove(entry)
            del self.__pin_names[arg]
        else:
            entry = PinEntry(arg, mode)
            self.__pins.remove(entry)
            if entry in self.__pin_names.values():
                key = next(i for i, e in self.__pin_names if e == entry)
                del self.__pin_names[key]

    """ methods delegated by behavior """

    def on_pin_update(self, pin: Pin[D], prev_state):
        self.behavior().on_pin_update(self, pin, prev_state)

    def on_comp_update(self, subcomp: Component, prev_state):
        self.behavior().on_comp_update(self, subcomp, prev_state)

    def on_state_update(self, state, prev_state):
        self.behavior().on_state_update(self, state, prev_state)

    def write_pin(self, pin: Pin[D], data: D):
        self.behavior().write_pin(self, pin, data)


if __name__ == '__main__':
    from logy.core.primitive.pin import Pin, PinBehavior
    from logy.core.primitive.wire import Wire, WireBehavior
    from logy.core.primitive.data import Data

    wires: List[Wire] = []
    comps: List[Component] = []


    class MyPinBehavior(PinBehavior):
        def on_data_update(self, pin: Pin, prev_state):
            print(f'Pin.on_data_update {pin.name}: {prev_state["data"]} -> {pin.data}')
            for w in wires:
                if PinEntry(pin, Mode.IN) in w.entries:
                    w.on_pin_write(pin, prev_state)
            for c in comps:
                if PinEntry(pin, Mode.IN) in c.entries:
                    c.on_pin_update(pin, prev_state)


    class MyWireBehavior(WireBehavior):
        def on_pin_update(self, wire: Wire, pin: Pin, prev_state):
            print(f'Wire.on_pin_update {pin.name} in {wire.name}')
            wire.data = pin.data
            for pin, mode in wire.entries:
                if mode is Mode.IN:
                    pin.write(wire.data)


    class MyComponentBehavior(ComponentBehavior):

        def on_pin_update(self, comp: Component, pin: Pin, prev_state):
            print(f'Component.on_pin_update {pin.name} in {comp}')
            for id, state in comp.pin_mapped.items():
                entry = comp.get_pin(id)
                if entry.pin is pin and entry.mode is Mode.IN:
                    comp.__setattr__(state, pin.data)

        def on_state_update(self, comp: Component, state, prev_state):
            print(f'Component.on_state_update in {comp}')
            updated = [st for st, value in state.items() if value != prev_state[st]]
            for st in updated:
                # state affects another state
                affected = comp.pin_affected.get(st, set())
                for aff_state in affected:
                    comp.__getattribute__(aff_state)

                # state affects pin
                for id, name in comp.pin_mapped.items():
                    entry = comp.get_pin(id)
                    if entry.mode is Mode.OUT:
                        comp.write_pin(entry.pin, state[st])

        def on_comp_update(self, comp: Component, subcomp: Component, prev_state):
            pass

        def write_pin(self, comp: Component, pin: Pin[D], data: D):
            pin.write(data)


    class MyComponent(Component):
        def __init__(self, pin_a: Pin, pin_b: Pin, pin_out: Pin, name: str = None):
            super().__init__([(pin_a, Mode.IN, 'a'), (pin_b, Mode.IN, 'b'),
                              (pin_out, Mode.OUT, 'out')], name=name)
            self.A, self.B, self.Out

        @Component.mapped('a', Mode.IN)
        def A(self, data: D) -> bool:
            return data.value == 1

        @Component.mapped('b', Mode.IN)
        def B(self, data: D) -> bool:
            return data.value == 1

        @Component.mapped('out', Mode.OUT, srcs=("A", "B"), eval=lambda a, b: a and b)
        def Out(self, value: bool) -> D:
            return Data(1) if value is True else Data(0)


    Pin.behavior = lambda _: MyPinBehavior()
    Wire.behavior = lambda _: MyWireBehavior()
    Component.behavior = lambda _: MyComponentBehavior()

    pin_in1 = Pin(Data(0), name="in_1")
    pin_in2 = Pin(Data(0), name="in_2")

    pin_out = Pin(Data(0), name="out")

    comp = MyComponent(pin_in1, pin_in2, pin_out, name='MyComponent')
    comps.append(comp)

    pin_in1.write(1)
    pin_in2.write(1)
    print(pin_out.data)
