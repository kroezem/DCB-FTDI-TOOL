import time
import gpio
import i2c
import jtag
from ftdi import Ftdi
from utilities import choose, hex_in, clear, yellow, red, line, blue, green, plain, bits
from pyftdi.ftdi import FtdiError
from pyftdi.usbtools import UsbToolsError
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
                modes = [
                    "GPIO",
                    'UART',
                    # 'JTAG',
                    'I2C'
                ]
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

        except (UsbToolsError, ValueError) as e:
            print(red("USB ERROR - DEVICE NOT CONNECTED OR FTDI DRIVERS NOT INSTALLED"))

            print("Type", blue("\"help\""), "for driver install instructions or", red("Enter"), "to retry.")
            if input(green(">>")).upper().strip() == "HELP":
                print("\nInstall", green("D2XX"), "and", green("VCP Drivers"), "->",
                      blue("https://ftdichip.com/wp-content/uploads/2021/08/CDM212364_Setup.zip"))
                print("\nDownload and open", green("Zadig"), "->",
                      blue("https://github.com/pbatard/libwdi/releases/download/v1.5.0/zadig-2.8.exe"))
                print("\nClick", green("options,"), "check", green("List all Devices"), "and uncheck",
                      green("Ignore Hubs or Composite Parents"))
                print("Select", green("USB <-> Serial Converter (Composite Parent)"), red("(FTDI DEVICE MUST BE CONNECTED)"))
                print("Select", green("libusb-win32"), red("(not WinUSB)"), " in the driver list")
                print("Click", green("Replace Driver"))
                print("\nMore info ->", blue("https://eblot.github.io/pyftdi/installation.html#windows"))
                input("\nPress " + red("Enter") + " to quit")
                exit(2)

        except KeyboardInterrupt:
            exit(2)
