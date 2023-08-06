from __future__ import annotations
from typeguard import typechecked
from typing import Optional, Union
from iqrfpy.enums.commands import UartRequestCommands
from iqrfpy.enums.message_types import UartMessages
from iqrfpy.enums.peripherals import EmbedPeripherals
from iqrfpy.exceptions import RequestParameterInvalidValueError
from iqrfpy.utils.dpa import BaudRates, BYTE_MIN, BYTE_MAX, HWPID_MAX
from iqrfpy.irequest import IRequest

__all__ = [
    'OpenRequest',
]


@typechecked
class OpenRequest(IRequest):

    __slots__ = '_baud_rate'

    def __init__(self, nadr: int, baud_rate: BaudRates, hwpid: int = HWPID_MAX, timeout: Optional[float] = None,
                 msgid: Optional[str] = None):
        self._validate(baud_rate=baud_rate)
        super().__init__(
            nadr=nadr,
            pnum=EmbedPeripherals.UART,
            pcmd=UartRequestCommands.OPEN,
            m_type=UartMessages.OPEN,
            hwpid=hwpid,
            timeout=timeout,
            msgid=msgid
        )
        self._baud_rate = baud_rate

    @staticmethod
    def _validate_baud_rate(baud_rate: BaudRates):
        if not (BYTE_MIN <= baud_rate <= BYTE_MAX):
            raise RequestParameterInvalidValueError('Baud rate value should be between 0 and 255.')

    def _validate(self, baud_rate: BaudRates):
        self._validate_baud_rate(baud_rate=baud_rate)

    def set_baud_rate(self, baud_rate: BaudRates):
        self._validate_baud_rate(baud_rate=baud_rate)
        self._baud_rate = baud_rate

    def to_dpa(self, mutable: bool = False) -> Union[bytes, bytearray]:
        self._pdata = [self._baud_rate]
        return super().to_dpa(mutable=mutable)

    def to_json(self) -> dict:
        self._params = {'baudRate': self._baud_rate}
        return super().to_json()
