import multiprocessing
import platform

from .system import SYSTEM

def choices():
    return range(1, multiprocessing.cpu_count() + 1)

def default():
    return max(1, multiprocessing.cpu_count() - 1)

__UNIX__ = """
export CPU_COUNT={{ number }}
if [[ "$SCONSFLAGS" = "" ]]; then
    export SCONSFLAGS="-j$CPU_COUNT"
else
    export SCONSFLAGS=$SCONSFLAGS" -j$CPU_COUNT"
fi
"""

__WIN__ = """
set CPU_COUNT={{ number }}
if "%SCONSFLAGS%"=="" (
    set SCONSFLAGS=-j%CPU_COUNT%
) else (
    set SCONSFLAGS=%SCONSFLAGS% -j%CPU_COUNT%
)
"""

def activate(number):
    if not isinstance(number, int) or number not in choices():
        raise ValueError("'number' should be an integer superior to 1 and inferior to " + str(multiprocessing.cpu_count()))
    elif not number == default():
        warning.warns()
    if SYSTEM == 'win':
        return __WIN__.replace("{{ number }}", str(number))
    elif SYSTEM in ['osx', 'linux']:
        return __UNIX__.replace("{{ number }}", str(number))

def deactivate():
    if SYSTEM == 'win':
        return 'set CPU_COUNT='
    elif SYSTEM in ['osx', 'linux']:
        return 'unset CPU_COUNT'