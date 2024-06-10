import time
from utilities import url, green, line, red
import threading


def read_from_port(serial_port, running):
    while running.is_set():
        data = serial_port.read(1024)
        if data:
            print("\n", red("<<"), data.decode('utf-8'), flush=True)
            print("\n", green(">>"))


def write_to_port(serial_port, running):
    while running.is_set():
        try:
            time.sleep(.5)
            user_input = input()
            if user_input:
                serial_port.write(user_input.encode('utf-8') + b'\n')
        except EOFError:
            # Handle EOFError if input() is interrupted
            return


def mode(ftdi):
    line('UART MINITERM')
    ftdi.pins['SOC_PWR'].set_value(1)
    ftdi.pins['FTDI_RDY_N'].set_value(0)
    ftdi.write()

    ftdi.uart.timeout = 0  # Non-blocking read
    running = threading.Event()
    running.set()  # Set the running event to signal that threads should run

    # Start the read thread
    read_thread = threading.Thread(target=read_from_port, args=(ftdi.uart, running))
    read_thread.daemon = True
    read_thread.start()

    # Start the write thread
    write_thread = threading.Thread(target=write_to_port, args=(ftdi.uart, running))
    write_thread.daemon = True
    write_thread.start()

    try:
        print("Press", red("CTRL-C"), "to exit")
        print(green(">>"))
        while True:
            time.sleep(0.1)  # Small delay to prevent high CPU usage

    except KeyboardInterrupt:
        print("Exiting...")
        running.clear()  # Signal threads to stop
        read_thread.join()  # Wait for the read thread to finish
        write_thread.join()  # Wait for the write thread to finish
