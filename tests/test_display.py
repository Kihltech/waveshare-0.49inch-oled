#!/usr/bin/env python3
"""
Display Test Suite

Hardware tests for the Waveshare 0.49" OLED module.
Run this to verify your display is working correctly.
"""

import sys
import time


def test_i2c_detection():
    """Test that the display is detected on I2C bus."""
    print("Test 1: I2C Detection")

    try:
        import smbus2
        bus = smbus2.SMBus(1)

        # Try to read from address 0x3C
        try:
            bus.read_byte(0x3C)
            print("  ✓ Display detected at 0x3C on bus 1")
            bus.close()
            return True
        except OSError:
            pass

        # Try bus 0
        bus.close()
        bus = smbus2.SMBus(0)
        try:
            bus.read_byte(0x3C)
            print("  ✓ Display detected at 0x3C on bus 0")
            bus.close()
            return True
        except OSError:
            pass

        bus.close()
        print("  ✗ Display not detected")
        return False

    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def test_luma_driver():
    """Test with luma.oled SSD1306 driver."""
    print("\nTest 2: luma.oled SSD1306 Driver")

    try:
        from luma.core.interface.serial import i2c
        from luma.oled.device import ssd1306
        from luma.core.render import canvas

        serial = i2c(port=1, address=0x3C)
        device = ssd1306(serial, width=64, height=32)

        # Test pattern
        with canvas(device) as draw:
            draw.rectangle(device.bounding_box, outline="white")
            draw.line((0, 0, 63, 31), fill="white")
            draw.line((0, 31, 63, 0), fill="white")

        time.sleep(1)
        device.clear()

        print("  ✓ luma.oled driver works correctly")
        return True

    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def test_standalone_driver():
    """Test standalone SSD1315 driver."""
    print("\nTest 3: Standalone SSD1315 Driver")

    try:
        from ssd1315 import SSD1315, canvas

        display = SSD1315()

        # Test pattern
        with canvas(display) as draw:
            draw.rectangle((0, 0, 63, 31), outline=1)
            draw.text((8, 12), "Test OK", fill=1)

        time.sleep(1)
        display.clear()
        display.display()
        display.close()

        print("  ✓ Standalone driver works correctly")
        return True

    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def test_pixel_corners():
    """Test that all corners are visible."""
    print("\nTest 4: Corner Visibility")

    try:
        from luma.core.interface.serial import i2c
        from luma.oled.device import ssd1306
        from luma.core.render import canvas

        serial = i2c(port=1, address=0x3C)
        device = ssd1306(serial, width=64, height=32)

        with canvas(device) as draw:
            # Corner pixels
            draw.point((0, 0), fill="white")
            draw.point((63, 0), fill="white")
            draw.point((0, 31), fill="white")
            draw.point((63, 31), fill="white")
            # Center
            draw.point((32, 16), fill="white")

        print("  Check: Are all 4 corners and center lit?")
        result = input("  (y/n): ").strip().lower()

        device.clear()

        if result == 'y':
            print("  ✓ All pixels addressable")
            return True
        else:
            print("  ✗ Pixel addressing issue")
            return False

    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def test_contrast():
    """Test contrast control."""
    print("\nTest 5: Contrast Control")

    try:
        from luma.core.interface.serial import i2c
        from luma.oled.device import ssd1306
        from luma.core.render import canvas

        serial = i2c(port=1, address=0x3C)
        device = ssd1306(serial, width=64, height=32)

        with canvas(device) as draw:
            draw.rectangle(device.bounding_box, fill="white")

        print("  Cycling contrast levels...")
        for level in [0, 64, 128, 192, 255, 128]:
            device.contrast(level)
            time.sleep(0.5)

        device.clear()
        print("  ✓ Contrast control works")
        return True

    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def main():
    print("=" * 50)
    print("Waveshare 0.49\" OLED Test Suite")
    print("=" * 50)

    results = []

    results.append(("I2C Detection", test_i2c_detection()))
    results.append(("luma.oled Driver", test_luma_driver()))
    results.append(("Standalone Driver", test_standalone_driver()))
    results.append(("Corner Visibility", test_pixel_corners()))
    results.append(("Contrast Control", test_contrast()))

    print("\n" + "=" * 50)
    print("Results Summary")
    print("=" * 50)

    passed = 0
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {name}: {status}")
        if result:
            passed += 1

    print(f"\nTotal: {passed}/{len(results)} tests passed")

    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
