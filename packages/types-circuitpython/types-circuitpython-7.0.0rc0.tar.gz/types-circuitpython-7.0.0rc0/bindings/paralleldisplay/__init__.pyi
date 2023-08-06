from __future__ import annotations

import microcontroller
from _typing import ReadableBuffer

class ParallelBus:
    """Manage updating a display over 8-bit parallel bus in the background while Python code runs. This
    protocol may be refered to as 8080-I Series Parallel Interface in datasheets. It doesn't handle
    display initialization."""

    def __init__(
        self,
        *,
        data0: microcontroller.Pin,
        command: microcontroller.Pin,
        chip_select: microcontroller.Pin,
        write: microcontroller.Pin,
        read: microcontroller.Pin,
        reset: microcontroller.Pin,
    ) -> None:
        """Create a ParallelBus object associated with the given pins. The bus is inferred from data0
        by implying the next 7 additional pins on a given GPIO port.

        The parallel bus and pins are then in use by the display until `displayio.release_displays()`
        is called even after a reload. (It does this so CircuitPython can use the display after your
        code is done.) So, the first time you initialize a display bus in code.py you should call
        :py:func:`displayio.release_displays` first, otherwise it will error after the first code.py run.

        :param microcontroller.Pin data0: The first data pin. The rest are implied
        :param microcontroller.Pin command: Data or command pin
        :param microcontroller.Pin chip_select: Chip select pin
        :param microcontroller.Pin write: Write pin
        :param microcontroller.Pin read: Read pin
        :param microcontroller.Pin reset: Reset pin"""
        ...
    def reset(self) -> None:
        """Performs a hardware reset via the reset pin. Raises an exception if called when no reset pin
        is available."""
        ...
    def send(self, command: int, data: ReadableBuffer) -> None:
        """Sends the given command value followed by the full set of data. Display state, such as
        vertical scroll, set via ``send`` may or may not be reset once the code is done."""
        ...
