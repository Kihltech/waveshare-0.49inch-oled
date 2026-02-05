#!/usr/bin/env python3
"""
Graphics Demo

Demonstrates various drawing capabilities on the Waveshare 0.49" OLED.
"""

import time
import math

from luma.core.interface.serial import i2c
from luma.oled.device import ssd1306
from luma.core.render import canvas


def demo_shapes(device):
    """Draw basic shapes."""
    print("  Shapes demo...")

    # Rectangle
    with canvas(device) as draw:
        draw.rectangle((2, 2, 30, 29), outline="white")
        draw.rectangle((34, 2, 61, 29), outline="white", fill="white")
    time.sleep(1.5)

    # Lines
    with canvas(device) as draw:
        for i in range(0, 64, 8):
            draw.line((i, 0, 63 - i, 31), fill="white")
    time.sleep(1.5)

    # Circles
    with canvas(device) as draw:
        draw.ellipse((2, 2, 29, 29), outline="white")
        draw.ellipse((34, 2, 61, 29), outline="white", fill="white")
    time.sleep(1.5)


def demo_animation(device):
    """Simple animation."""
    print("  Animation demo...")

    # Bouncing ball
    x, y = 10, 16
    dx, dy = 2, 1

    for _ in range(50):
        with canvas(device) as draw:
            draw.ellipse((x - 3, y - 3, x + 3, y + 3), fill="white")

        x += dx
        y += dy

        if x <= 3 or x >= 60:
            dx = -dx
        if y <= 3 or y >= 28:
            dy = -dy

        time.sleep(0.05)


def demo_text(device):
    """Text display demo."""
    print("  Text demo...")

    messages = ["Waveshare", "0.49 OLED", "SSD1315", "64x32 px"]

    for msg in messages:
        with canvas(device) as draw:
            # Center text (approximate)
            x = (64 - len(msg) * 6) // 2
            draw.text((x, 12), msg, fill="white")
        time.sleep(1)


def demo_scrolling_text(device):
    """Scrolling text demo."""
    print("  Scrolling text demo...")

    text = "Waveshare 0.49\" OLED Module with SSD1315 Controller    "

    for offset in range(len(text) * 6):
        with canvas(device) as draw:
            draw.text((-offset, 12), text + text, fill="white")
        time.sleep(0.03)


def demo_sine_wave(device):
    """Animated sine wave."""
    print("  Sine wave demo...")

    for phase in range(0, 360, 5):
        with canvas(device) as draw:
            for x in range(64):
                y = int(16 + 12 * math.sin(math.radians(x * 6 + phase)))
                draw.point((x, y), fill="white")
        time.sleep(0.02)


def main():
    print("Graphics Demo - Waveshare 0.49\" OLED\n")

    serial = i2c(port=1, address=0x3C)
    device = ssd1306(serial, width=64, height=32)

    demos = [
        ("Basic Shapes", demo_shapes),
        ("Text Display", demo_text),
        ("Scrolling Text", demo_scrolling_text),
        ("Animation", demo_animation),
        ("Sine Wave", demo_sine_wave),
    ]

    try:
        for name, demo_func in demos:
            print(f"\n{name}:")
            demo_func(device)
            time.sleep(0.5)

    except KeyboardInterrupt:
        print("\nInterrupted")

    finally:
        device.clear()
        print("\nDone!")


if __name__ == "__main__":
    main()
