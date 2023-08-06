from __future__ import annotations

class IS31FL3741:
    """Displays an in-memory framebuffer to a IS31FL3741 drive display."""

    def __init__(self, *, width: int) -> None:
        """Create a IS31FL3741 object with the given attributes.

        The framebuffer is in "RGB888" format using 4 bytes per pixel.
        Bits 24-31 are ignored. The format is in RGB order.

        If a framebuffer is not passed in, one is allocated and initialized
        to all black.  In any case, the framebuffer can be retrieved
        by passing the Is31fl3741 object to memoryview().

        A Is31fl3741 is often used in conjunction with a
        `framebufferio.FramebufferDisplay`."""
    def deinit(self) -> None:
        """Free the resources associated with this
        IS31FL3741 instance.  After deinitialization, no further operations
        may be performed."""
        ...
    brightness: float
    """In the current implementation, 0.0 turns the display off entirely
    and any other value up to 1.0 turns the display on fully."""

    def refresh(self) -> None:
        """Transmits the color data in the buffer to the pixels so that
        they are shown."""
        ...
    width: int
    """The width of the display, in pixels"""

    height: int
    """The height of the display, in pixels"""
