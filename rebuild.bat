python -m PyInstaller main.py --add-data "libusb0.dll;." --hidden-import=pyftdi.serialext.protocol_ftdi --hidden-import=libusb --onefile --icon=icon.ico -n=FTDI-TOOL

