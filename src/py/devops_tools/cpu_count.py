import multiprocessing
import platform

from .system import SYSTEM

def get_range_cpu_count():
    return range(1, multiprocessing.cpu_count() + 1)

def get_default_cpu_count():
    return max(1, multiprocessing.cpu_count() - 1)

def activate_cpu_count(cpu_count):
    if not isinstance(cpu_count, int) or cpu_count not in get_range_cpu_count():
        raise ValueError("'cpu_count' should be an integer superior to 1 and inferior to " + str(multiprocessing.cpu_count()))
    elif not cpu_count == get_default_cpu_count():
        warning.warns()
    if SYSTEM == 'win':
        return 'set CPU_COUNT=' + str(cpu_count)
    elif SYSTEM in ['osx', 'linux']:
        return 'export CPU_COUNT=' + str(cpu_count)

def deactivate_cpu_count():
    if SYSTEM == 'win':
        return 'set CPU_COUNT='
    elif SYSTEM in ['osx', 'linux']:
        return 'unset CPU_COUNT'