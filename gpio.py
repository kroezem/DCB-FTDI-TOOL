import jtag
from utilities import choose, hex_in, clear, yellow, red, line, blue, green, plain, bits
from pyftdi.ftdi import FtdiError
import time


def mode(ftdi):
    try:
        while True:
            line('GPIO MODE')

            commands = [
                "set_defaults",
                "set_direction",
                "read",
                "write",
                "fpga_version",
                "platform_pwr_cycle",
                "jtag_clk",
                # "all_IO_help",
            ]

            command = choose('TYPE NUMBER OR COMMAND', commands)
            match command:
                case "set_defaults":
                    line('SET DEFAULTS')
                    ftdi.set_default()
                    ftdi.read()

                case "set_direction":
                    line('SET DIRECTION')

                    pins = list(ftdi.pins.keys())
                    pins.remove("DVIEW_SEL_1")
                    pins.remove("DVIEW_SEL_2")

                    directions = []
                    for pin in pins:
                        if ftdi.pins[pin].direction == 1:
                            directions.append(red('OUT'))
                        elif ftdi.pins[pin].direction == 0:
                            directions.append(blue('IN '))

                    pin = choose("CHOOSE PIN", pins, directions)

                    if pin:
                        direction = choose("SET DIRECTION", ['IN', 'OUT'])
                        if direction:
                            if pin == 'DVIEW_SEL_0':
                                ftdi.pins["DVIEW_SEL_1"].set_direction(direction == 'OUT')
                                ftdi.pins["DVIEW_SEL_2"].set_direction(direction == 'OUT')

                            ftdi.pins[pin].set_direction(direction == 'OUT')
                            ftdi.set_direction()

                        else:
                            print(red("Cancelled"))
                    else:
                        print(red("Cancelled"))

                case "read":
                    line('READ')
                    ftdi.read()

                case "write":
                    line('WRITE')

                    outputs = []
                    values = []
                    for pin in ftdi.pins.keys():
                        if ftdi.pins[pin].direction == 1:
                            outputs.append(pin)
                            if ftdi.pins[pin].value == 1:
                                values.append(red('HIGH'))
                            elif ftdi.pins[pin].value == 0:
                                values.append(blue('LOW '))

                    pin = choose("CHOOSE PIN", outputs, values)
                    if pin:
                        value = choose("SET " + blue(pin) + yellow(" VALUE"), ['LOW', 'HIGH'])
                        if value:
                            ftdi.pins[pin].set_value(value == 'HIGH')
                            ftdi.write()
                        else:
                            print(red("Cancelled"))
                    else:
                        print(red("Cancelled"))

                case "fpga_version":
                    line("FPGA VERSION")
                    print("Version:", ftdi.fpga_version())

                case "platform_pwr_cycle":
                    line("PLATFORM POWER CYCLE")
                    print("Powering Off...")
                    ftdi.pins['ATX_PWR_CYCLE'].set_direction(1)
                    ftdi.pins['ATX_PWR_CYCLE'].set_value(1)
                    ftdi.set_direction()
                    ftdi.write()

                    for i in range(5):
                        time.sleep(1)
                        ftdi.bus[1].read()
                        print('.', end='', flush=True)

                    print("\nfailed")

                case "jtag_clk":
                    jtag.mode(ftdi)

                case _:
                    break

    except KeyboardInterrupt:
        print("Exiting...")
