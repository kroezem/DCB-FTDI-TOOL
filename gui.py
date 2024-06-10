import time

import cutie
from utilities import clear, yellow, red, line, blue

import gpio
from pyftdi.ftdi import FtdiError
from pyftdi.i2c import I2cController
from pyftdi.gpio import GpioAsyncController
from pyftdi.gpio import GpioMpsseController

# --proxy="http://proxy-chain.intel.com:911"

""" THIS IS A DISCARDED VERSION THAT HAD ARROW KEY NAVIGATION, NO LONGER WORKS  """


def pin_defaults():
    return {
        "   FTDI PINS:  ": gpio.Comment(),
        "JTAG_CLK       ": gpio.Pin(bus[1], 0, 1, 0),
        "ATX_PWR_CYCLE  ": gpio.Pin(bus[1], 7, 1, 0),
        "SOC_PWR        ": gpio.Pin(bus[1], 6, 1, 0),
        "SRST_N         ": gpio.Pin(bus[1], 5, 1, 1),
        "SRST_N_state   ": gpio.Pin(bus[4], 1, 0, 0),
        "FTDI_RDY_N     ": gpio.Pin(bus[4], 7, 1, 1),
        "GPIO_0         ": gpio.Pin(bus[2], 3, 0, 1),
        "GPIO_1         ": gpio.Pin(bus[2], 5, 0, 1),

        "\n   FPGA PINS:": gpio.Comment(),
        "A0_DEBUG       ": gpio.Pin(bus[0], 0, 0, 0),
        "BOOT_MODE      ": gpio.Pin(bus[0], 1, 0, 0),
        "DFT_TAP_SEL    ": gpio.Pin(bus[0], 2, 0, 0),
        "INTEL_TEST_MODE": gpio.Pin(bus[0], 3, 0, 0),
        "DVIEW_SEL_0    ": gpio.Pin(bus[0], 4, 0, 0),
        "DVIEW_SEL_1    ": gpio.Pin(bus[0], 5, 0, 0),
        "DVIEW_SEL_2    ": gpio.Pin(bus[0], 6, 0, 0),
        "FTDI_JTAG      ": gpio.Pin(bus[0], 7, 1, 0),

    }


i2c = I2cController()
io0 = gpio.I2cAdapter()
io1 = GpioAsyncController()
# io3 = GpioAsyncController()
io4 = GpioAsyncController()

bus = {}
pins = {}


def connect():
    i2c.configure('ftdi:///2')

    io0.configure(i2c.get_port(0x56))  # Pass controller to adapter
    io1.configure('ftdi:///1')
    io2 = i2c.get_gpio()
    # io3.configure('ftdi:///3')
    io4.configure('ftdi:///4')

    global bus
    bus = {
        0: gpio.Bus(io0, 0b00000000, 0b00000000),
        1: gpio.Bus(io1, 0b00110001, 0b11110001),
        2: gpio.Bus(io2, 0b00000000, 0b00000011, 0x78),
        # 3: gpio.Bus(io3, 0b00110001, 0b11110001),
        4: gpio.Bus(io4, 0b00110001, 0b11110001),
    }


def close():
    i2c.close()
    io1.close()
    io4.close()


def set_dir():
    pin_list = list(pins.keys())  # List of all pins

    # Remove DVIEW 1&2 as they will follow direction of DVIEW 0
    pin_list.remove("DVIEW_SEL_1    ")
    pin_list.remove("DVIEW_SEL_2    ")

    ticked = []
    comments = []
    for i, pin in enumerate(pin_list):  # Get ticked list to have indices of all outputs
        pins[pin].update()  # Update all pins to current values
        if pins[pin].direction is None:
            comments.append(i)
        if pins[pin].direction == 1:
            ticked.append(i)

    print(yellow('   DIR  GPIO'))  # Header
    selected = cutie.select_multiple(  # Menu
        pin_list,
        deselected_ticked_prefix=red('   OUT  '),
        deselected_unticked_prefix=blue('   IN   '),
        selected_ticked_prefix=" >" + red(' OUT  '),
        selected_unticked_prefix=" >" + blue(' IN   '),
        ticked_indices=ticked,
        caption_indices=comments,
    )
    print()

    selected = [pin_list[pin] for pin in selected]  # changing selected from indexes to pin names
    for pin in pin_list:
        pins[pin].set_direction(pin in selected)  # Iterate through pins, set value to reflect selected list

    pins["DVIEW_SEL_1    "].set_direction(pins["DVIEW_SEL_0    "].direction)  # force 1,2 to reflect dir of 0
    pins["DVIEW_SEL_2    "].set_direction(pins["DVIEW_SEL_0    "].direction)

    for b in bus.values():
        b.set_direction()  # Tell each bus to write their direction to the direction register


def write():
    options = []  # Get list of all outputs

    for pin in list(pins.keys()):
        pins[pin].update()  # Make sure pin has current values
        if pins[pin].direction != 0:
            options.append(pin)

    ticked = []  # Get a list of indices where the value of the pin is high
    comments = []
    for i, pin in enumerate(options):
        if pins[pin].value is None:
            comments.append(i)
        if pins[pin].value == 1:
            ticked.append(i)

    print(yellow('   VAL  GPIO'))  # Header
    selected = cutie.select_multiple(  # Menu
        options,
        deselected_ticked_prefix=red('    1  '),
        deselected_unticked_prefix=blue('    0  '),
        selected_ticked_prefix=" >" + red('  1  '),
        selected_unticked_prefix=" >" + blue('  0  '),
        ticked_indices=ticked,
        caption_indices=comments,
    )
    print()

    selected = [options[pin] for pin in selected]  # Convert list of selected indices to a list of pin names
    for pin in options:
        pins[pin].set_value(pin in selected)  # Iterate through outputs, set value to reflect selected list

    for b in bus.values():
        b.write()  # Tell each bus to write their values to the output register


def read():
    for b in bus.values():
        b.read()  # Update busses to current values

    print(yellow('\n   VAL  DIR   GPIO'))  # Header
    # print(yellow('\n   DIR  VAL  GPIO'))  # Header
    for pin in list(pins.keys()):
        pins[pin].update()  # Update pin to current values

        if pins[pin].value == 1:  # Values
            print('    ' + red('1'), end='')
        elif pins[pin].value == 0:
            print('    ' + blue('0'), end='')

        if pins[pin].direction == 1:  # Directions
            print('   ' + red('OUT') + '   ', end='')
        elif pins[pin].direction == 0:
            print('   ' + blue('IN ') + '   ', end='')

        print(pin)


def set_default():
    global pins
    pins = pin_defaults()  # Overwrite pins with defaults

    for pin in pins.values():  # Write all pin values to buses
        pin.set_direction()
        pin.set_value()

    for b in bus.values():  # Write buses to registers
        b.set_direction()
        b.write()


def gpio_mode():
    command = 0
    try:
        while True:
            # clear()
            line('GPIO MODE')

            commands = [
                "set_defaults",
                "set_direction",
                "read",
                "write",
                "fpga_ver",
                "platform_pwr_cycle",
                "all_IO_help",
                red('back')
            ]

            print(yellow('   COMMANDS'))
            command = cutie.select(
                commands,
                deselected_prefix="   ",
                selected_prefix=blue(' > '),
                selected_index=command
            )

            match commands[command]:
                case "set_defaults":
                    clear()
                    line('SET DEFAULTS')
                    set_default()
                    read()
                    # input('\n enter to continue')

                case "set_direction":
                    clear()
                    line('SET DIRECTION')
                    set_dir()
                    read()

                case "read":
                    clear()
                    line('READ')
                    read()
                    # input('\n enter to continue')

                case "write":
                    clear()
                    line('WRITE')
                    write()
                    read()
                    # input('\n enter to continue')

                case "fpga_ver":
                    clear()
                    line("FPGA VERSION")
                    print("Version:", io0.fpga_ver())

                case "platform_pwr_cycle":
                    clear()
                    line("PLATFORM POWER CYCLE")
                    print("Powering Off")
                    pins['ATX_PWR_CYCLE  '].set_direction(1)
                    pins['ATX_PWR_CYCLE  '].set_value(1)
                    bus[1].set_direction()
                    bus[1].write()
                    break

                case _:
                    break
    except FtdiError:
        print('Device disconnected\n')


def uart_mode():
    pass


def i2c_mode():
    pass


if __name__ == "__main__":
    mode = 0
    clear()
    while True:
        # clear()
        close()

        line('FTDI TOOL')
        print(yellow('   MODES'))
        modes = ["GPIO", "JTAG", 'UART', 'I2C', red('quit')]
        mode = cutie.select(
            modes,
            deselected_prefix="   ",
            selected_prefix=blue(' > '),
            selected_index=mode
        )

        match modes[mode]:
            case "GPIO":
                # Need to uncomment this to configure the buses GPIO connection

                # if len(ftdi.check()) > 0:
                #     print("\nConnected to ", ftdi.check()[0][0].sn)
                #     ftdi.start()
                #     gpio_mode()
                # else:
                #     print("\nNo FTDI device connected")

                connect()
                set_default()
                time.sleep(.1)
                read()
                gpio_mode()
            case "JTAG":
                pass

            case "UART":
                uart_mode()
            case "I2C":
                i2c_mode()
            case _:
                break
