from typing import *
from ..core.component import *


class CircuitDesigner:
    def __init__(self):
        self.__comp = None
        self.__pin = None

    @property
    def comp(self) -> 'CircuitDesigner.ComponentAccess':
        if self.__comp is None:
            self.__comp = CircuitDesigner.ComponentAccess()
        return self.__comp

    @property
    def pin(self) -> 'CircuitDesigner.PinAccess':
        if self.__pin is None:
            self.__pin = CircuitDesigner.PinAccess()
        return self.__pin

    class ComponentAccess:
        def __init__(self):
            self.comps: Dict[str, Component] = {}

        def __getattr__(self, key: str):
            return self.comps.get(key)

        def __setattr__(self, key: str, value: Component):
            self.comps[key] = value



    class PinAccess:
        def __init__(self):
            self.pin_by_name: Dict[str, Pin] = {}
            self.pin_by_index: Dict[int, Pin] = {}

        def __getattr__(self, key: str):
            return self.pin_by_name.get(key)

        def __setattr__(self, key: str, value: Pin):
            self.pin_by_name[key] = value

        def __getitem__(self, index: int):
            return self.pin_by_index.get(index, None)

        def __setitem__(self, index: int, value: Pin):
            self.pin_by_index[index] = value


designer = CircuitDesigner()
designer.pins.regs = Pin()