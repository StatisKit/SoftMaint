import multiprocessing
import platform

from .system import SYSTEM

def choices():
    return range(1, multiprocessing.cpu_count() + 1)

def default():
    return max(1, multiprocessing.cpu_count() - 1)

def activate(number):
    if not isinstance(number, int) or number not in choices():
        raise ValueError("'number' should be an integer superior to 1 and inferior to " + str(multiprocessing.cpu_count()))
    elif not number == default():
        warning.warns()
    if SYSTEM == 'win':
        return 'set CPU_COUNT=' + str(number)
    elif SYSTEM in ['osx', 'linux']:
        return 'export CPU_COUNT=' + str(number)

def deactivate():
    if SYSTEM == 'win':
        return 'set CPU_COUNT='
    elif SYSTEM in ['osx', 'linux']:
        return 'unset CPU_COUNT'        