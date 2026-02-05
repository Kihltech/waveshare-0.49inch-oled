#!/usr/bin/env python3
"""
Hello World Example

Basic demonstration of the Waveshare 0.49" OLED display.
Shows both luma.oled and standalone driver usage.
"""

import time


def example_with_luma():
    """Using luma.oled library (recommended)."""
    print("Example 1: Using luma.oled library")

    from luma.core.interface.serial import i2c
    from luma.oled.device import ssd1306
    from luma.core.render import canvas

    serial = i2c(port=1, address=0x3C)
    device = ssd1306(serial, width=64, height=32)

    with canvas(device) as draw:
        draw.rectangle(device.bounding_box, outline="white", fill="black")
        draw.text((8, 4), "Hello", fill="white")
        draw.text((8, 16), "World!", fill="white")

    print("  Display shows 'Hello World!'")
    time.sleep(3)
    device.clear()


def example_with_standalone():
    """Using standalone driver."""
    print("Example 2: Using standalone driver")

    from ssd1315 import SSD1315, canvas

    display = SSD1315()

    with canvas(display) as draw:
        draw.rectangle((0, 0, 63, 31), outline=1, fill=0)
        draw.text((8, 4), "Hello", fill=1)
        draw.text((8, 16), "World!", fill=1)

    print("  Display shows 'Hello World!'")
    time.sleep(3)
    display.clear()
    display.display()
    display.close()


if __name__ == "__main__":
    print("Waveshare 0.49\" OLED - Hello World\n")

    try:
        example_with_luma()
    except ImportError:
        print("  luma.oled not installed, skipping...")

    print()

    try:
        example_with_standalone()
    except ImportError as e:
        print(f"  Standalone driver error: {e}")

    print("\nDone!")
