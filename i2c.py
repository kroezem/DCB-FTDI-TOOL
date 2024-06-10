from utilities import choose, hex_in, int_in, clear, yellow, red, line, blue, green, plain, bits


def mode(ftdi):
    line('I2C MODE')
    print("Press", red("CTRL-C"), "to exit\n")

    try:
        address = hex_in('Port Address (hex): 0x')
        slave = ftdi.i2c.get_port(address[0])

        while True:
            commands = ['READ', 'WRITE']
            command = choose('\nTYPE NUMBER OR COMMAND', commands)
            match command:
                case 'READ':
                    offset = hex_in('Address Offset (hex): 0x')

                    length = int_in('Read Length (int): ')

                    print('\n', green('>>'), slave.read_from(offset[0], length))

                case 'WRITE':
                    offset = hex_in('Address Offset (hex): 0x')

                    data = hex_in('Data (hex): 0x')

                    slave.write_to(offset[0], data)

                case _:
                    break

    except KeyboardInterrupt:
        print("\nExiting...")
