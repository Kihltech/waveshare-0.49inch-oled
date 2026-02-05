#!/usr/bin/env python3
"""
SSD1315 OLED Driver

Standalone driver for SSD1315-based OLED displays.
Developed for the Waveshare 0.49" OLED Module (64x32 pixels).

The SSD1315 is highly compatible with SSD1306 and uses the same command set.
This driver can also be used with other SSD1315-based displays by adjusting
the width and height parameters.

Example usage:
    from ssd1315 import SSD1315, canvas

    display = SSD1315()

    with canvas(display) as draw:
        draw.text((0, 0), "Hello!", fill=1)

Author: Robert Kihlberg / Kihltech
Repository: https://github.com/Kihltech/waveshare-0.49inch-oled
License: MIT
"""

import smbus2
from PIL import Image, ImageDraw


class SSD1315:
    """
    SSD1315 OLED display driver.

    Args:
        bus: I2C bus number (default: 1)
        address: I2C address (default: 0x3C)
        width: Display width in pixels (default: 64)
        height: Display height in pixels (default: 32)
        rotate: Rotation - 0 for normal, 2 for 180° (default: 0)
    """

    # Command constants
    DISPLAY_OFF = 0xAE
    DISPLAY_ON = 0xAF
    SET_CLOCK_DIV = 0xD5
    SET_MUX_RATIO = 0xA8
    SET_DISPLAY_OFFSET = 0xD3
    SET_START_LINE = 0x40
    CHARGE_PUMP = 0x8D
    CHARGE_PUMP_ON = 0x14
    SET_MEMORY_MODE = 0x20
    SEG_REMAP_ON = 0xA1
    SEG_REMAP_OFF = 0xA0
    COM_SCAN_DEC = 0xC8
    COM_SCAN_INC = 0xC0
    SET_COM_PINS = 0xDA
    SET_CONTRAST = 0x81
    SET_PRECHARGE = 0xD9
    SET_VCOMH = 0xDB
    DISPLAY_ALL_ON_RESUME = 0xA4
    NORMAL_DISPLAY = 0xA6
    INVERSE_DISPLAY = 0xA7
    SET_COLUMN_ADDR = 0x21
    SET_PAGE_ADDR = 0x22

    def __init__(
        self,
        bus: int = 1,
        address: int = 0x3C,
        width: int = 64,
        height: int = 32,
        rotate: int = 0,
    ):
        self.bus = smbus2.SMBus(bus)
        self.address = address
        self.width = width
        self.height = height
        self.rotate = rotate
        self.pages = height // 8
        self._buffer = [0] * (width * self.pages)

        self._init_display()

    def _command(self, *cmds):
        """Send command byte(s) to the display."""
        for cmd in cmds:
            self.bus.write_byte_data(self.address, 0x00, cmd)

    def _data(self, data_bytes):
        """Send data bytes to the display."""
        chunk_size = 32
        for i in range(0, len(data_bytes), chunk_size):
            chunk = list(data_bytes[i:i + chunk_size])
            self.bus.write_i2c_block_data(self.address, 0x40, chunk)

    def _init_display(self):
        """Initialize the display."""
        # Display off
        self._command(self.DISPLAY_OFF)

        # Clock divide ratio / oscillator frequency
        self._command(self.SET_CLOCK_DIV, 0x80)

        # Multiplex ratio
        self._command(self.SET_MUX_RATIO, self.height - 1)

        # Display offset
        self._command(self.SET_DISPLAY_OFFSET, 0x00)

        # Display start line
        self._command(self.SET_START_LINE | 0x00)

        # Charge pump enable
        self._command(self.CHARGE_PUMP, self.CHARGE_PUMP_ON)

        # Memory addressing mode: horizontal
        self._command(self.SET_MEMORY_MODE, 0x00)

        # Segment remap and COM scan direction based on rotation
        if self.rotate == 0:
            self._command(self.SEG_REMAP_ON)
            self._command(self.COM_SCAN_DEC)
        else:  # rotate == 2 (180 degrees)
            self._command(self.SEG_REMAP_OFF)
            self._command(self.COM_SCAN_INC)

        # COM pins configuration
        com_pins = 0x02 if self.height <= 32 else 0x12
        self._command(self.SET_COM_PINS, com_pins)

        # Contrast
        self._command(self.SET_CONTRAST, 0xCF)

        # Pre-charge period
        self._command(self.SET_PRECHARGE, 0xF1)

        # VCOMH deselect level
        self._command(self.SET_VCOMH, 0x40)

        # Resume from RAM content
        self._command(self.DISPLAY_ALL_ON_RESUME)

        # Normal display
        self._command(self.NORMAL_DISPLAY)

        # Display on
        self._command(self.DISPLAY_ON)

        # Clear and update
        self.clear()
        self.display()

    def clear(self):
        """Clear the frame buffer."""
        self._buffer = [0] * (self.width * self.pages)

    def display(self):
        """Write frame buffer to display."""
        self._command(self.SET_COLUMN_ADDR, 0, self.width - 1)
        self._command(self.SET_PAGE_ADDR, 0, self.pages - 1)
        self._data(self._buffer)

    def set_pixel(self, x: int, y: int, color: int = 1):
        """
        Set a single pixel.

        Args:
            x: X coordinate (0 to width-1)
            y: Y coordinate (0 to height-1)
            color: 0 for off, 1 for on
        """
        if 0 <= x < self.width and 0 <= y < self.height:
            page = y // 8
            bit = y % 8
            idx = page * self.width + x

            if color:
                self._buffer[idx] |= (1 << bit)
            else:
                self._buffer[idx] &= ~(1 << bit)

    def fill(self, color: int = 1):
        """
        Fill entire display.

        Args:
            color: 0 for black, 1 for white
        """
        self._buffer = [0xFF if color else 0x00] * (self.width * self.pages)

    def image(self, img: Image.Image):
        """
        Display a PIL Image.

        Args:
            img: PIL Image object (will be converted to 1-bit)
        """
        if img.mode != '1':
            img = img.convert('1')

        if img.size != (self.width, self.height):
            img = img.resize((self.width, self.height))

        self.clear()
        pixels = img.load()
        for y in range(self.height):
            for x in range(self.width):
                if pixels[x, y]:
                    self.set_pixel(x, y, 1)

    def contrast(self, level: int):
        """
        Set display contrast.

        Args:
            level: Contrast level (0-255)
        """
        self._command(self.SET_CONTRAST, level & 0xFF)

    def invert(self, enable: bool = True):
        """
        Invert display colors.

        Args:
            enable: True to invert, False for normal
        """
        self._command(self.INVERSE_DISPLAY if enable else self.NORMAL_DISPLAY)

    def power(self, on: bool = True):
        """
        Turn display on or off.

        Args:
            on: True for on, False for off
        """
        self._command(self.DISPLAY_ON if on else self.DISPLAY_OFF)

    def close(self):
        """Clean up resources."""
        self.power(False)
        self.bus.close()


class Canvas:
    """
    Context manager for drawing on the display using PIL.

    Usage:
        with Canvas(display) as draw:
            draw.text((0, 0), "Hello", fill=1)
            draw.rectangle((0, 0, 10, 10), outline=1)
    """

    def __init__(self, device: SSD1315):
        self.device = device
        self.image = Image.new('1', (device.width, device.height), 0)
        self.draw = ImageDraw.Draw(self.image)

    def __enter__(self) -> ImageDraw.ImageDraw:
        return self.draw

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.device.image(self.image)
        self.device.display()
        return False


def canvas(device: SSD1315) -> Canvas:
    """
    Create a canvas context manager for drawing.

    Args:
        device: SSD1315 display instance

    Returns:
        Canvas context manager
    """
    return Canvas(device)
