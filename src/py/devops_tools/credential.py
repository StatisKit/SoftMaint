import getpass
import warnings
import netrc
import os

from .system import SYSTEM

from . import config

__CACHE__ = None

def _filename(filename=None):
    if filename is None:
        if SYSTEM == 'win':
            filename = os.path.join(os.environ.get("USERPROFILE"), "_netrc")
        else:
            filename = os.path.join(os.environ.get("HOME"), ".netrc")
    return filename

def load(filename=None):
    global __CACHE__
    if __CACHE__ is None or filename is not None:
        if __CACHE__ is None:
            __CACHE__ = dict()
        filename = _filename(filename=filename)
        try:
            credentials = netrc.netrc(file=filename)
            for host, (login, account, password) in credentials.hosts.iteritems():
                __CACHE__[host] = dict(login = login,
                                       account = account,
                                       password = password)
        except Exception as e:
            __CACHE__ = dict()

def register(filename=None):
    global __CACHE__
    filename = _filename(filename=filename)
    with open(filename, "w") as filehandler:
        for host, credential in __CACHE__.iteritems():
            filehandler.write("machine " + host + "\n")
            if __CACHE__[host]["login"]:
                filehandler.write("login " + credential["login"] + "\n")
            if __CACHE__[host]["account"]:
                filehandler.write("account " + credential["account"] + "\n")
            if __CACHE__[host]["password"]:
                filehandler.write("password " + credential["password"] + "\n")

def retrieve(host, login='', password='', stdin=True):
    global __CACHE__
    load()
    if not login:
        if not host is None:
            try:
                login = __CACHE__[host]["login"]
            except:
                warnings.warn("login and/or password for '" + host + "' host has not been found in the '" + _filename() + "' file.", UserWarning)
        if not login and stdin:
            sentence = "login for '" + host + "': "
            login = raw_input(sentence)
            if password:
                while not login:
                    warnings.warn('Invalid login...', UserWarning)
                    login = raw_input(sentence)
    if login:
        if not password:
            if not host is None:
                try:
                    password = __CACHE__[host]["password"]
                except:
                    if login == "TOKEN":
                        warnings.warn("token for '" + host + "' host has not been found in the '" + _filename() + "' file.", UserWarning)
                    else:
                        warnings.warn("login and/or password for '" + host + "' host has not been found in the '" + _filename() + "' file.", UserWarning)
                if not password and stdin:
                    if not login == "TOKEN":
                        sentence = login + "'s password"
                    else:
                        sentence = "token"
                    sentence += " for '" + host + "': "
                    password = getpass.getpass(sentence)
                    while not password:
                        if login == "TOKEN":
                            warnings.warn('Invalid token...', UserWarning)
                        else:
                            warnings.warn('Invalid password...', UserWarning)
                        password = getpass.getpass(sentence)
    else:
        login = ''
        password = ''
    __CACHE__[host] = dict(login = login,
                           password = password,
                           account = None)
    config.load()
    if config.__CACHE__.get("netrc_update", False):
        register()
    return login, password