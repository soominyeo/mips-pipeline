from abc import abstractmethod, ABC
from typing import Iterable, Union, Tuple

from logy.core.primitive import Component, Pin, Mode, D, BinaryData
from logy.core.primitive.data import Mode, D, BinaryData


class SyncComponent(Component, ABC):
    def __init__(self, pins: Iterable[Union[Tuple[Pin, Mode, str]]] = (), components: Iterable[Component] = (),
                 name: str = None):
        self.__pin_clk = Pin(BinaryData(0, length=1), name="CLK")
        super().__init__([*pins, (self.__pin_clk, Mode.IN, "CLK")], components, name=name)
        self.clk

    @property
    def pin_clk(self):
        return self.__pin_clk

    @Component.mapped("CLK", Mode.IN)
    def clk(self, data: D) -> bool:
        return data.value == 1

    def update(self, state):
        super().update(state)
        if 'clk' in state.keys() and state['clk'] != self.clk:
            if self.clk:
                self.rising_edge()
            else:
                self.falling_edge()

    def rising_edge(self):
        return

    def falling_edge(self):
        return


