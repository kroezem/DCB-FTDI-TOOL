pyinstaller main.py --add-data "libusb0.dll;." --hidden-import=pyftdi.serialext.protocol_ftdi --onefile

