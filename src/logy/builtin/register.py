from typing import Optional

from logy.core.component import Component, Pin


class Register(Component, classifier="REG"):
    def __init__(self, size: int, name: Optional[str] = None):
        super(Register, self).__init__(([Pin('reg_write'), Pin('reg_clock')], [Pin("reg_read")]), name=name)
        self.__size = size
        self.__data = 0
        self.

    def _validate(self, value: int) -> bool:
        return 0 <= value < 2 ** self.__size

    @property
    def data(self):
        return self.__data

    @data.setter
    def data(self, value: int):
        if not self._validate(value):
            raise AttributeError
        self.__data = value

