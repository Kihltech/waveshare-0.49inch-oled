#!/usr/bin/env python3
"""
System Monitor Example

Displays CPU temperature and load on the Waveshare 0.49" OLED.
Press Ctrl+C to exit.
"""

import subprocess
import time

from luma.core.interface.serial import i2c
from luma.oled.device import ssd1306
from luma.core.render import canvas


def get_cpu_temp():
    """Get CPU temperature."""
    try:
        result = subprocess.run(
            ['vcgencmd', 'measure_temp'],
            capture_output=True,
            text=True
        )
        temp = result.stdout.replace("temp=", "").replace("'C\n", "")
        return f"{temp}C"
    except Exception:
        return "N/A"


def get_cpu_load():
    """Get CPU load percentage."""
    try:
        with open('/proc/loadavg', 'r') as f:
            load = f.read().split()[0]
            return f"{float(load)*100/4:.0f}%"  # Assuming 4 cores
    except Exception:
        return "N/A"


def get_memory_usage():
    """Get memory usage percentage."""
    try:
        with open('/proc/meminfo', 'r') as f:
            lines = f.readlines()
            total = int(lines[0].split()[1])
            available = int(lines[2].split()[1])
            used_percent = (total - available) / total * 100
            return f"{used_percent:.0f}%"
    except Exception:
        return "N/A"


def main():
    print("System Monitor - Waveshare 0.49\" OLED")
    print("Press Ctrl+C to exit\n")

    serial = i2c(port=1, address=0x3C)
    device = ssd1306(serial, width=64, height=32)

    try:
        while True:
            temp = get_cpu_temp()
            load = get_cpu_load()
            mem = get_memory_usage()

            with canvas(device) as draw:
                draw.text((0, 0), f"T:{temp}", fill="white")
                draw.text((0, 11), f"C:{load}", fill="white")
                draw.text((0, 22), f"M:{mem}", fill="white")

            time.sleep(2)

    except KeyboardInterrupt:
        print("\nExiting...")
        device.clear()


if __name__ == "__main__":
    main()
