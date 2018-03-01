import os
import yaml

from .system import SYSTEM

__CACHE__ = None

def _filename(filename=None):
    if filename is None:
        if SYSTEM == 'win':
            filename = os.path.join(os.environ.get("USERPROFILE"), "_devopsrc")
        else:
            filename = os.path.join(os.environ.get("HOME"), ".devopsrc")
    return filename

def load(filename=None):
    global __CACHE__
    if __CACHE__ is None or filename is not None:
        filename = _filename(filename=filename)
        try:
            with open(filename, "r") as filehandler:
                __CACHE__ = yaml.load(filehandler.read())
        except Exception as e:
            __CACHE__ = dict()

def register(filename=None):
    global __CACHE__
    load()
    filename = _filename(filename=filename)
    with open(filename, "w") as filehandler:
        filehandler.write(yaml.dump(__CACHE__, default_flow_style=False))

def set_active_branch(branch):
    global __CACHE__
    load()
    if not active_branch is None:
        __CACHE__["active_branch"] = branch

def unset_active_branch():
    global __CACHE__
    load()
    __CACHE__.pop("active_branch", None)
    
def set_netrc_update(update=False):
    global __CACHE__
    load()
    if update is not None:
        __CACHE__["netrc_update"] = update

