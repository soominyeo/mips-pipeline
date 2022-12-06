from typing import Optional, Generic

from logy.core.component import Component, Pin, BinaryData


class Register(Component, classifier="REG"):
    def __init__(self, bit_length: int, name: Optional[str]):
        super(Register, self).__init__(name=name)
        self.clk = Pin(BinaryData(0, 1))
        self.data = Mu



