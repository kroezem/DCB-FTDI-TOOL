import time
import gpio
import i2c
import jtag
from ftdi import Ftdi
from utilities import choose, hex_in, clear, yellow, red, line, blue, green, plain, bits
from pyftdi.ftdi import FtdiError
from sys import exit
import uart

ftdi = Ftdi()

if __name__ == "__main__":
    clear()
    while True:
        try:
            ftdi.connect()
            while True:
                line('FTDI TOOL')
                ftdi.update()
                modes = ["GPIO", "JTAG", 'UART', 'I2C']
                mode = choose('TYPE NUMBER OR MODE', modes)
                match mode:
                    case "GPIO":
                        gpio.mode(ftdi)

                    case "JTAG":
                        jtag.mode(ftdi)

                    case "UART":
                        uart.mode(ftdi)

                    case "I2C":
                        i2c.mode(ftdi)

                    case None:
                        exit(2)

        except FtdiError as e:
            ftdi.close()
            print(red("FAILED TO CONNECT"))
            input("Press " + blue("Enter") + " to Retry")
        except KeyboardInterrupt:
            exit(2)
        #
        # except Exception as e:
        #     print(e)
        #     input("Press " + blue("Enter") + " to Retry\n")

