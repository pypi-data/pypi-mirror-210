"""Supervisor settings"""

from __future__ import annotations

from typing import Optional

runtime: Runtime
"""Runtime information, such as ``runtime.serial_connected``
(USB serial connection status).
This object is the sole instance of `supervisor.Runtime`."""

def enable_autoreload() -> None:
    """Enable autoreload based on USB file write activity."""
    ...

def disable_autoreload() -> None:
    """Disable autoreload based on USB file write activity until
    `enable_autoreload` is called."""
    ...

def set_rgb_status_brightness(brightness: int) -> None:
    """Set brightness of status neopixel from 0-255
    `set_rgb_status_brightness` is called."""
    ...

def reload() -> None:
    """Reload the main Python code and run it (equivalent to hitting Ctrl-D at the REPL)."""
    ...

def set_next_stack_limit(size: int) -> None:
    """Set the size of the stack for the next vm run. If its too large, the default will be used."""
    ...

def set_next_code_file(
    filename: Optional[str],
    *,
    reload_on_success: bool = False,
    reload_on_error: bool = False,
    sticky_on_success: bool = False,
    sticky_on_error: bool = False,
    sticky_on_reload: bool = False,
) -> None:
    """Set what file to run on the next vm run.

    When not ``None``, the given ``filename`` is inserted at the front of the usual ['code.py',
    'main.py'] search sequence.

    The optional keyword arguments specify what happens after the specified file has run:

    ``sticky_on_…`` determine whether the newly set filename and options stay in effect: If
    True, further runs will continue to run that file (unless it says otherwise by calling
    ``set_next_code_filename()`` itself). If False, the settings will only affect one run and
    revert to the standard code.py/main.py afterwards.

    ``reload_on_…`` determine how to continue: If False, wait in the usual "Code done running.
    Waiting for reload. / Press any key to enter the REPL. Use CTRL-D to reload." state. If
    True, reload immediately as if CTRL-D was pressed.

    ``…_on_success`` take effect when the program runs to completion or calls ``sys.exit()``.

    ``…_on_error`` take effect when the program exits with an exception, including the
    KeyboardInterrupt caused by CTRL-C.

    ``…_on_reload`` take effect when the program is interrupted by files being written to the USB
    drive (auto-reload) or when it calls ``supervisor.reload()``.

    These settings are stored in RAM, not in persistent memory, and will therefore only affect
    soft reloads. Powering off or resetting the device will always revert to standard settings.

    When called multiple times in the same run, only the last call takes effect, replacing any
    settings made by previous ones. This is the main use of passing ``None`` as a filename: to
    reset to the standard search sequence."""
    ...

class RunReason:
    """The reason that CircuitPython started running."""

    STARTUP: object
    """CircuitPython started the microcontroller started up. See `microcontroller.Processor.reset_reason`
       for more detail on why the microcontroller was started."""

    AUTO_RELOAD: object
    """CircuitPython restarted due to an external write to the filesystem."""

    SUPERVISOR_RELOAD: object
    """CircuitPython restarted due to a call to `supervisor.reload()`."""

    REPL_RELOAD: object
    """CircuitPython started due to the user typing CTRL-D in the REPL."""

class Runtime:
    """Current status of runtime objects.

    Usage::

       import supervisor
       if supervisor.runtime.serial_connected:
           print("Hello World!")"""

    def __init__(self) -> None:
        """You cannot create an instance of `supervisor.Runtime`.
        Use `supervisor.runtime` to access the sole instance available."""
        ...
    usb_connected: bool
    """Returns the USB enumeration status (read-only)."""

    serial_connected: bool
    """Returns the USB serial communication status (read-only)."""

    serial_bytes_available: int
    """Returns the whether any bytes are available to read
    on the USB serial input.  Allows for polling to see whether
    to call the built-in input() or wait. (read-only)"""

    run_reason: RunReason
    """Returns why CircuitPython started running this particular time."""
