import os

from . import credential


def retrieve(login=None, password=None):
    login, password = credential.retrieve('anaconda.org',
                                          login=login,
                                          password=password)
    credential.__CACHE__['anaconda.org'] = dict(login = login,
                                                password = password,
                                                account = None)
    return login, password

def current_prefix():
    return os.environ['CONDA_PREFIX']

def default_prefix():
    prefix = current_prefix()
    while not os.path.exists(os.path.join(os.path.dirname(prefix), 'envs')):
        prefix = os.path.dirname(prefix)
    return os.path.dirname(prefix)

def current_environment():
    return os.environ['CONDA_DEFAULT_ENV']