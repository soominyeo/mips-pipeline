from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Generic, Optional, TYPE_CHECKING, Collection

if TYPE_CHECKING:
    from logy.core.component.primitive import Element

from logy.core.component.data import D, D1, D2


class Receivable(Generic[D], ABC):
    """An interface class capable of receiving data."""

    def __init__(self, default: Optional[D]):
        super().__init__(default)
        self.__inbound = None

    @property
    def inbound(self):
        class Access:
            def __init__(self, master: 'Receivable[D]'):
                self.__master = master

            def __getitem__(self, item):
                return self.__master._get_inbound(item)

            def __setitem__(self, key, value):
                self.__master._set_inbound(key, value)

            def __delitem__(self, key):
                self.__master._del_inbound(key)

        if self.__inbound is None:
            self.__inbound = Access(self)
        return self.__inbound

    @abstractmethod
    def _get_inbound(self, source: 'Transmittable[D]') -> Optional[D]:
        """Get inbound data from the source"""

    @abstractmethod
    def _set_inbound(self, source: 'Transmittable[D]', value: Optional[D]):
        """Set inbound data from the source"""

    @abstractmethod
    def _del_inbound(self, source: 'Transmittable[D]'):
        """Delete inbound data from the source"""

    def write(self, data: D, actor: Optional['Transmittable[D]'] = None):
        """
        Write data to the receivable.
        :param data: data to write
        :param actor: the transmitter trying to write data
        """
        self.inbound[actor] = data

    def erase(self, actor: Optional['Transmittable[D]'] = None):
        """
        Erase data incoming from a specific transmittable.
        :param actor: the transmitter trying to erase its data to the receivable
        """
        del self.inbound[actor]


class Transmittable(Generic[D], ABC):
    """An interface class capable of sending data."""

    def __init__(self, default: Optional[D]):
        self.__default = default
        self.__outbound = None

    @property
    def outbound(self):
        """Get outbound data buffer access object for get/set/delete """

        class Access:
            def __init__(self, master: 'Transmittable[D]'):
                self.__master = master

            def __getitem__(self, item):
                return self.__master._get_outbound(item)

            def __setitem__(self, key, value):
                self.__master._set_outbound(key, value)

            def __delitem__(self, key):
                self.__master._del_outbound(key)

        if self.__outbound is None:
            self.__outbound = Access(self)
        return self.__outbound

    @abstractmethod
    def _get_outbound(self, dest: 'Receivable[D]') -> Optional[D]:
        """Get outbound data toward the destination."""

    @abstractmethod
    def _set_outbound(self, dest: 'Receivable[D]', value: Optional[D]):
        """Set outbound data toward the destination."""

    @abstractmethod
    def _del_outbound(self, dest: 'Receivable[D]'):
        """Delete outbound data from the destination."""

    def read(self, actor: Optional['Element'] = None) -> D:
        """
        Read data from the transmittable.
        :param actor: the receivable trying to read data
        :return: read data
        """
        return self.outbound[actor] or self.__default
