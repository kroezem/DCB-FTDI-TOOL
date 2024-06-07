import time

import pyftdi.ftdi

from utilities import clear, yellow, red, line, blue, url

from pyftdi.ftdi import UsbTools
from pyftdi.ftdi import FtdiError
from pyftdi.i2c import I2cController
from pyftdi.gpio import GpioAsyncController
from pyftdi.jtag import JtagEngine
from pyftdi import serialext



class Ftdi:
    """Main FTDI object"""
    def __init__(self):
        """Initialize FTDI device interfaces for I2C, JTAG, and UART, and define default bus configurations."""
        self.i2c = I2cController()
        self.jtag = JtagEngine(trst=True, frequency=15E6)
        self.uart = None

        self.bus = {
            0: Bus(I2cAdapter(), 0b00000000, 0b00000000),
            1: Bus(GpioAsyncController(), 0b00110001, 0b11110001),
            2: Bus(None, 0b00000000, 0b00000011, 0x78),
            4: Bus(GpioAsyncController(), 0b00110001, 0b11110001),
        }

        self.pins = self.pin_defaults()

    def pin_defaults(self):
        """Define the default state and direction for each pin used in the FTDI interface."""
        return {
            # "JTAG_CLK": Pin(self.bus[1], 0, 1, 0),
            "ATX_PWR_CYCLE": Pin(self.bus[1], 7, 1, 0),
            "SOC_PWR": Pin(self.bus[1], 6, 1, 0),
            "SRST_N": Pin(self.bus[1], 5, 1, 1),
            "SRST_N_state": Pin(self.bus[4], 1, 0, 0),
            "FTDI_RDY_N": Pin(self.bus[4], 7, 1, 1),
            "GPIO_0": Pin(self.bus[2], 3, 0, 1),
            "GPIO_1": Pin(self.bus[2], 5, 0, 1),

            "A0_DEBUG": Pin(self.bus[0], 0, 0, 0),
            "BOOT_MODE": Pin(self.bus[0], 1, 0, 0),
            "DFT_TAP_SEL": Pin(self.bus[0], 2, 0, 0),
            "INTEL_TEST_MODE": Pin(self.bus[0], 3, 0, 0),
            "DVIEW_SEL_0": Pin(self.bus[0], 4, 0, 0),
            "DVIEW_SEL_1": Pin(self.bus[0], 5, 0, 0),
            "DVIEW_SEL_2": Pin(self.bus[0], 6, 0, 0),
            # "FTDI_JTAG": Pin(self.bus[0], 7, 1, 0),
        }

    def connect(self):
        """Configure all controllers with FTDI urls"""
        UsbTools.release_all_devices()
        UsbTools.flush_cache()

        self.i2c.configure(url(2))
        self.jtag.configure(url(1))
        self.uart = serialext.serial_for_url(url(3), baudrate=3000000)

        self.bus[0].controller.configure(self.i2c.get_port(0x56))  # Pass controller to adapter
        self.bus[1].controller.configure(url(1))
        self.bus[2].controller = self.i2c.get_gpio()
        self.bus[4].controller.configure(url(4))

        # make sure this pin is set low, otherwise stuck in infinite reset loop
        self.pins['ATX_PWR_CYCLE'].set_value(0)

    def close(self):
        """Close connections"""
        self.i2c.close()
        self.jtag.close()
        self.bus[1].controller.close()
        self.bus[4].controller.close()

    def set_direction(self):
        """Write bus directions to all controllers"""
        for b in self.bus.values():
            b.set_direction()  # Tell each bus to write their direction to the direction register

    def write(self):
        """Write bus values to all controllers"""
        for b in self.bus.values():
            b.write()  # Tell each bus to write their values to the output register

    def read(self):
        """Updates values from and prints a table"""
        for b in self.bus.values():
            b.read()  # Update busses to current values

        print(yellow('   VAL  DIR   GPIO'))  # Header
        for pin in list(self.pins.keys()):
            self.pins[pin].update()  # Update pin to current values

            if self.pins[pin].value == 1:  # Values
                print('    ' + red('1'), end='')
            elif self.pins[pin].value == 0:
                print('    ' + blue('0'), end='')

            if self.pins[pin].direction == 1:  # Directions
                print('   ' + red('OUT') + '   ', end='')
            elif self.pins[pin].direction == 0:
                print('   ' + blue('IN ') + '   ', end='')

            print(pin)

    def set_default(self):
        """Overwrite pins with defaults"""
        self.pins = self.pin_defaults()
        self.update()

    def update(self):
        """Forces every pin and bus to the correct state"""
        for pin in self.pins.values():  # Write all pin values to buses
            pin.set_direction()
            pin.set_value()

        for b in self.bus.values():  # Write buses to controllers
            b.set_direction()
            b.write()

    def fpga_version(self):
        """Grabs FPGA version using I2Cadapter"""
        return self.bus[0].controller.fpga_ver()


class Pin:
    """User facing pin definitions"""
    def __init__(self, bus, bit, direction, value):
        self.bus = bus
        self.bit = bit
        self.direction = direction
        self.value = value

    def set_direction(self, direction=None):
        """Update pin direction and push to bus"""
        if direction is not None:
            self.direction = int(direction)

        if self.direction:
            self.bus.direction |= (1 << self.bit)
        else:
            self.bus.direction &= ~(1 << self.bit)

    def set_value(self, value=None):
        """Update pin value and push to bus"""
        if value is not None:
            self.value = int(value)

        if self.value:
            self.bus.value |= (1 << self.bit)
        else:
            self.bus.value &= ~(1 << self.bit)

    def update(self):
        """Update pin value from bus"""
        self.value = (self.bus.value >> self.bit) & 1


class I2cAdapter:
    # This adapter allows for the control of the FPGA's GPIO using the same methods as other GPIO
    def __init__(self):
        self.controller = None

    def fpga_ver(self):
        return self.controller.read_from(0x00, 1)[0]

    def configure(self, controller):
        self.controller = controller

    def read(self):
        return self.controller.read_from(0x10, 1)[0]

    def write(self, value):
        self.controller.write_to(0x12, value.to_bytes(1))

    def set_direction(self, mask, direction):
        self.controller.write_to(0x11, direction.to_bytes(1))

    def debug(self):
        print("\n   INPUTS:", '{:08b}'.format(self.controller.read_from(0x10, 1)[0]))
        print("DIRECTION:", '{:08b}'.format(self.controller.read_from(0x11, 1)[0]))
        print("  OUTPUTS:", '{:08b}'.format(self.controller.read_from(0x12, 1)[0]))

    def close(self):
        """This is only here so the adapter mimics other controllers"""
        pass


class Bus:
    """FPGA facing bus definitions"""
    def __init__(self, controller, value, direction, mask=0xFF):
        self.controller = controller
        self.direction = direction
        self.value = value
        self.mask = mask

    def read(self):
        """Read bus values from FTDI controller"""
        # For some reason I2CGpio is the only one that masks the output bits, so we need to disable that
        if self.mask != 0xFF:
            self.value = self.controller.read(True)
        else:
            self.value = self.controller.read()

        return self.value

    def write(self):
        """Write bus values to FTDI controller"""
        self.controller.write(self.value & self.direction)

    def set_direction(self):
        """Write bus directions to FTDI controller"""
        self.controller.set_direction(self.mask, self.direction)
