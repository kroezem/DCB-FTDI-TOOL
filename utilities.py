from colorama import Fore
from colorama import Style
import shutil
import re

import os


def url(port):
    out = os.environ.get('FTDI_DEVICE', 'ftdi://ftdi:4232/' + str(port))
    return out


def hex_in(prompt):
    while True:
        try:
            return [int(num, 16) for num in input(prompt).strip().split(' ')]
        except ValueError:
            print(red("INVALID INPUT"))


def int_in(prompt):
    while True:
        try:
            return int(input(prompt).strip())
        except ValueError:
            print(red("INVALID INPUT"))


def bits(num):
    print('{:08b}'.format(num))


def choose(prompt, options, values=None):
    if values is None:
        values = []
    original = list(options)
    longest = max(len(option) for option in original)

    options = [white("{: <{}}".format(option, longest)) for option in options]
    numbers = [green("{: >3}".format(i)) for i in range(len(options))]
    options.append(red("{: <5}".format('back')))
    numbers.append(green("{: >3}".format('Z')))

    print(yellow(prompt))
    for i, mode in enumerate(options):
        try:
            # row = [pink("{: >3}".format(i)), white("{: <{}}".format(mode, longest)), values[i]]
            row = [numbers[i], options[i], values[i]]
            print("{} {} {}".format(*row))
        except IndexError:
            row = [numbers[i], options[i]]
            print("{} {}".format(*row))
        # print('  ' + pink(i) + '  ' + mode )0

    options = [plain(option).upper().strip() for option in options]
    numbers = [plain(number).upper().strip() for number in numbers]
    while True:
        chosen = input(green(">>")).strip().upper()

        if chosen == 'Z' or chosen == 'BACK':
            return None

        if chosen in options:
            return original[options.index(chosen)]

        try:
            if chosen in numbers:
                return original[numbers.index(chosen)]
        except ValueError:
            pass

        print(red('INVALID CHOICE'))


def clear():
    os.system('cls' if os.name == 'nt' else 'clear')


def plain(text):
    pattern = re.compile(r'\x1b\[[0-9;]*m')
    return pattern.sub('', text)


def white(text):
    return f"{Fore.LIGHTWHITE_EX}" + str(text) + f"{Style.RESET_ALL}"


def red(text):
    return f"{Fore.LIGHTRED_EX}" + str(text) + f"{Style.RESET_ALL}"


def blue(text):
    return f"{Fore.CYAN}" + str(text) + f"{Style.RESET_ALL}"


def yellow(text):
    return f"{Fore.LIGHTYELLOW_EX}" + str(text) + f"{Style.RESET_ALL}"


def green(text):
    return f"{Fore.LIGHTGREEN_EX}" + str(text) + f"{Style.RESET_ALL}"


def line(text):
    # print('\n\033[4m' + text + ' ' * (os.get_terminal_size().columns - len(text)) + '\033[0m\n')
    whitespace = (shutil.get_terminal_size().columns - len(str(text))) - 2
    print(
        '\n' + '─' * int(whitespace / 2) + ' ' + str(text) + ' ' + '─' * int(whitespace / 2) + '─' * (
                whitespace % 2) + '\n')
