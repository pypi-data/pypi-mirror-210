"""USB Human Interface Device

The `usb_hid` module allows you to output data as a HID device."""

from __future__ import annotations

from typing import Optional, Sequence, Tuple

from _typing import ReadableBuffer

devices: Tuple[Device, ...]
"""Tuple of all active HID device interfaces.
The default set of devices is ``Device.KEYBOARD, Device.MOUSE, Device.CONSUMER_CONTROL``,
On boards where `usb_hid` is disabled by default, `devices` is an empty tuple.
"""

def disable() -> None:
    """Do not present any USB HID devices to the host computer.
    Can be called in ``boot.py``, before USB is connected.
    The HID composite device is normally enabled by default,
    but on some boards with limited endpoints, including STM32F4,
    it is disabled by default. You must turn off another USB device such
    as `usb_cdc` or `storage` to free up endpoints for use by `usb_hid`.
    """

def enable(devices: Optional[Sequence[Device]]) -> None:
    """Specify which USB HID devices that will be available.
    Can be called in ``boot.py``, before USB is connected.

    :param Sequence devices: `Device` objects.
      If `devices` is empty, HID is disabled. The order of the ``Devices``
      may matter to the host. For instance, for MacOS, put the mouse device
      before any Gamepad or Digitizer HID device or else it will not work.

    If you enable too many devices at once, you will run out of USB endpoints.
    The number of available endpoints varies by microcontroller.
    CircuitPython will go into safe mode after running ``boot.py`` to inform you if
    not enough endpoints are available.
    """
    ...

class Device:
    """HID Device specification"""

    def __init__(
        self,
        *,
        descriptor: ReadableBuffer,
        usage_page: int,
        usage: int,
        report_ids: Sequence[int],
        in_report_lengths: Sequence[int],
        out_report_lengths: Sequence[int],
    ) -> None:
        """Create a description of a USB HID device. The actual device is created when you
        pass a `Device` to `usb_hid.enable()`.

        :param ReadableBuffer report_descriptor: The USB HID Report descriptor bytes. The descriptor is not
          not verified for correctness; it is up to you to make sure it is not malformed.
        :param int usage_page: The Usage Page value from the descriptor. Must match what is in the descriptor.
        :param int usage: The Usage value from the descriptor. Must match what is in the descriptor.
        :param int report_ids: Sequence of report ids used by the descriptor.
          If the ``report_descriptor`` does not have a report ID, use 0.
        :param int in_report_lengths: Sequence of sizes in bytes of the HIDs report sent to the host.
          The sizes are in order of the ``report_ids``.
          "IN" is with respect to the host.
        :param int out_report_lengths: Size in bytes of the HID report received from the host.
          The sizes are in order of the ``report_ids``.
          "OUT" is with respect to the host.

        ``report_ids``, ``in_report_lengths``, and ``out_report_lengths`` must all be the same length.
        """
        ...
    KEYBOARD: Device
    """Standard keyboard device supporting keycodes 0x00-0xDD, modifiers 0xE-0xE7, and five LED indicators.
    Uses Report ID 1 for its IN and OUT reports.
    """

    MOUSE: Device
    """Standard mouse device supporting five mouse buttons, X and Y relative movements from -127 to 127
    in each report, and a relative mouse wheel change from -127 to 127 in each report.
    Uses Report ID 2 for its IN report.
    """

    CONSUMER_CONTROL: Device
    """Consumer Control device supporting sent values from 1-652, with no rollover.
    Uses Report ID 3 for its IN report."""

    def send_report(self, buf: ReadableBuffer, report_id: Optional[int] = None) -> None:
        """Send an HID report. If the device descriptor specifies zero or one report id's,
        you can supply `None` (the default) as the value of ``report_id``.
        Otherwise you must specify which report id to use when sending the report.
        """
        ...
    def get_last_received_report(self, report_id: Optional[int] = None) -> bytes:
        """Get the last received HID OUT report for the given report ID.
        The report ID may be omitted if there is no report ID, or only one report ID.
        Return `None` if nothing received.
        """
        ...
    last_received_report: bytes
    """The HID OUT report as a `bytes` (read-only). `None` if nothing received.
    Same as `get_last_received_report()` with no argument.

    Deprecated: will be removed in CircutPython 8.0.0. Use `get_last_received_report()` instead.
    """

    usage_page: int
    """The device usage page identifier, which designates a category of device. (read-only)"""

    usage: int
    """The device usage identifier, which designates a specific kind of device. (read-only)

    For example, Keyboard is 0x06 within the generic desktop usage page 0x01.
    Mouse is 0x02 within the same usage page."""
