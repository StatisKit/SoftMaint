import getpass
import warnings

def login(service, username='', password=''):
    if not username:
        username = raw_input(service + " Username: ")
        if password:
            while not username:
                warnings.warn('Invalid Username...', UserWarning)
                username = raw_input(service + " Username: ")
    if username:
        if not password:
            password = getpass.getpass(username + '\'s Password for ' + service + ': ')
            while not password:
                warnings.warn('Invalid Passsword...', UserWarning)
                password = getpass.getpass(username + '\'s Password for ' + service + ': ')
    else:
        username = ''
        password = ''
    return username, password