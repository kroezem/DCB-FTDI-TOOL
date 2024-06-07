from utilities import choose, hex_in, clear, yellow, red, line, blue, green, plain, bits
from pyftdi.bits import BitSequence


def mode(ftdi):
    try:
        line('JTAG CLOCK')
        ftdi.pins['SOC_PWR'].set_value(1)
        ftdi.pins['FTDI_RDY_N'].set_value(0)
        ftdi.write()
        ftdi.jtag.reset()

        dummy_data = BitSequence('0', length=10)

        print("Press", red("CTRL-C"), "to exit")
        print("\nWriting Dummy Data")
        while True:
            ftdi.jtag.write(dummy_data)

    except KeyboardInterrupt:
        print("Exiting...")