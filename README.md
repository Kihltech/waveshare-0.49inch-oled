# Waveshare 0.49" OLED Module Driver

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![AI Assisted](https://img.shields.io/badge/AI%20Assisted-95%25-blueviolet)](https://claude.ai)
[![Raspberry Pi](https://img.shields.io/badge/Raspberry%20Pi-3B%2B%20%2F%204B-C51A4A)](https://www.raspberrypi.com/)
[![Debian](https://img.shields.io/badge/Debian-12%20Bookworm-A81D33)](https://www.debian.org/)
[![Debian](https://img.shields.io/badge/Debian-13%20Trixie-A81D33)](https://www.debian.org/)
[![Python](https://img.shields.io/badge/Python-3.x-3776AB)](https://www.python.org/)

Python driver for the [Waveshare 0.49inch OLED Module](https://www.waveshare.com/wiki/0.49inch_OLED_Module) with SSD1315 controller, designed for Raspberry Pi.

## Hardware Specifications

| Specification | Value |
|---------------|-------|
| Controller | SSD1315 |
| Display Resolution | 64 × 32 pixels |
| Interface | I2C |
| I2C Address | 0x3C (default) |
| Operating Voltage | 3.3V / 5V |
| Display Size | 0.49" diagonal |
| Display Color | White |

## Compatibility

The SSD1315 controller is highly compatible with SSD1306. This module works with:
- The `luma.oled` library using the `ssd1306` device with `width=64, height=32`
- The standalone driver provided in this repository

Tested on:
- Raspberry Pi 4B
- Raspberry Pi 5
- Debian 12 (Bookworm), Debian 13 (Trixie)
- Python 3.9+

## Wiring

Connect the OLED module to your Raspberry Pi:

| OLED Pin | RPi Pin | RPi Function |
|----------|---------|--------------|
| VCC (red) | Pin 1 | 3.3V |
| SDA (green) | Pin 3 | GPIO 2 (I2C1 SDA) |
| SCL (yellow) | Pin 5 | GPIO 3 (I2C1 SCL) |
| GND (black) | Pin 6 | Ground |

## Installation

### Prerequisites

Enable I2C on your Raspberry Pi:
```bash
sudo raspi-config
# Navigate to: Interface Options -> I2C -> Enable
sudo reboot
```

Verify the display is detected:
```bash
sudo apt install -y i2c-tools
i2cdetect -y 1
# Should show device at address 0x3c
```

### Setup

Clone the repository and create a virtual environment:
```bash
git clone https://github.com/Kihltech/waveshare-0.49inch-oled.git
cd waveshare-0.49inch-oled

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
```

## Usage

### Quick Start with luma.oled

The simplest way to use this display is with the `luma.oled` library:

```python
from luma.core.interface.serial import i2c
from luma.oled.device import ssd1306
from luma.core.render import canvas

# Initialize display
serial = i2c(port=1, address=0x3C)
device = ssd1306(serial, width=64, height=32)

# Draw something
with canvas(device) as draw:
    draw.rectangle(device.bounding_box, outline="white", fill="black")
    draw.text((4, 8), "Hello!", fill="white")
```

### Using the Standalone Driver

This repository also includes a standalone driver:

```python
from ssd1315 import SSD1315, canvas

# Initialize display
display = SSD1315()

# Draw using PIL canvas
with canvas(display) as draw:
    draw.rectangle((0, 0, 63, 31), outline=1)
    draw.text((4, 8), "Hello!", fill=1)

# Or use direct pixel manipulation
display.clear()
display.set_pixel(32, 16, 1)
display.display()
```

### Example: System Monitor

```python
from luma.core.interface.serial import i2c
from luma.oled.device import ssd1306
from luma.core.render import canvas
import subprocess
import time

serial = i2c(port=1, address=0x3C)
device = ssd1306(serial, width=64, height=32)

def get_cpu_temp():
    result = subprocess.run(['vcgencmd', 'measure_temp'], capture_output=True, text=True)
    return result.stdout.replace("temp=", "").replace("'C\n", "°C")

while True:
    with canvas(device) as draw:
        draw.text((0, 0), "CPU Temp:", fill="white")
        draw.text((0, 16), get_cpu_temp(), fill="white")
    time.sleep(2)
```

## API Reference

### SSD1315 Class

```python
SSD1315(
    bus=1,           # I2C bus number
    address=0x3C,    # I2C address
    width=64,        # Display width
    height=32,       # Display height
    rotate=0         # Rotation (0, 2 for 180°)
)
```

**Methods:**
- `clear()` — Clear the frame buffer
- `display()` — Write frame buffer to display
- `set_pixel(x, y, color)` — Set a single pixel (color: 0 or 1)
- `fill(color)` — Fill entire display
- `image(pil_image)` — Display a PIL Image
- `contrast(level)` — Set contrast (0-255)
- `invert(enable)` — Invert display colors
- `power(on)` — Turn display on/off
- `close()` — Clean up resources

### canvas() Context Manager

```python
with canvas(display) as draw:
    # draw is a PIL ImageDraw object
    draw.text((x, y), "text", fill=1)
    draw.rectangle((x1, y1, x2, y2), outline=1, fill=0)
    draw.line((x1, y1, x2, y2), fill=1)
    draw.ellipse((x1, y1, x2, y2), outline=1)
```

## Files

| File | Description |
|------|-------------|
| `ssd1315.py` | Standalone SSD1315 driver module |
| `examples/hello_world.py` | Basic "Hello World" example |
| `examples/system_monitor.py` | CPU temperature display |
| `examples/graphics_demo.py` | Graphics demonstration |
| `tests/test_display.py` | Hardware test suite |

## Troubleshooting

### Display not detected
```bash
# Check I2C is enabled
ls /dev/i2c*

# Scan for devices
i2cdetect -y 1

# Check wiring and try again
```

### Permission denied
```bash
# Add user to i2c group
sudo usermod -aG i2c $USER
# Log out and back in
```

### Display shows garbage
- Verify `width=64, height=32` parameters
- Check wiring connections
- Try power cycling the display

## References

- [Waveshare 0.49" OLED module](https://www.waveshare.com/0.49inch-oled-module.htm)
- [Waveshare Wiki](https://www.waveshare.com/wiki/0.49inch_OLED_Module)
- [SSD1315 Datasheet](https://cursedhardware.github.io/epd-driver-ic/SSD1315.pdf)
- [luma.oled Documentation](https://luma-oled.readthedocs.io/)

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [luma.oled](https://github.com/rm-hull/luma.oled) project for the excellent OLED library
- Waveshare for hardware documentation
