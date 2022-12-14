from logy.builtin.clock import SyncComponent
from logy.core.primitive import Component, Pin, BinaryData, Mode, D, BufferedElement, BD, ComponentBehavior
from logy.core.test import Test


class Register(SyncComponent, BufferedElement[ComponentBehavior, BD], classifier="_REG"):
    def __init__(self, data: BD, name: str = None, is_rising_edge=True):
        self.__pin_data_in = Pin(data.of(None), name="DIN")
        self.__pin_data_out = Pin(data.of(None), name="DOUT")
        SyncComponent.__init__(self, [(self.__pin_data_in, Mode.IN, "DIN"),
                                      (self.__pin_data_out, Mode.OUT, "DOUT")], name=name)
        BufferedElement.__init__(self, data, name=self.name)
        self.is_rising_edge = is_rising_edge

        self.data_in
        self.data_out

    @property
    def pin_data_in(self):
        return self.__pin_data_in

    @property
    def pin_data_out(self):
        return self.__pin_data_out

    @Component.mapped("DIN", Mode.IN)
    def data_in(self, data: D) -> D:
        return data

    @Component.mapped("DOUT", Mode.OUT, srcs=['data'], eval=lambda d: d)
    def data_out(self, value: D) -> D:
        return value

    def rising_edge(self):
        if self.is_rising_edge:
            print('rising-edge')
            self.data = self.data_in

    def falling_edge(self):
        if not self.is_rising_edge:
            self.data = self.data_in


if __name__ == '__main__':
    test = Test()

    reg = Register(BinaryData(0, default=0, length=16))
    test.add_comp(reg)
    print(test.pins)

    reg.pin_data_in.write(65535)
    reg.pin_clk.write(1)
    reg.pin_clk.write(0)
    reg.pin_data_in.write(1)
    print(reg.pin_data_out)
    reg.pin_clk.write(1)
    print(reg.pin_data_out)
