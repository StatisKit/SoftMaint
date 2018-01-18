import os

def get_current_prefix():
    return os.environ['CONDA_PREFIX']

def get_default_prefix():
    prefix = get_current_prefix()
    while not os.path.exists(os.path.join(os.path.dirname(prefix), 'envs')):
        prefix = os.path.dirname(prefix)
    return os.path.dirname(prefix)

def get_current_environment():
    return os.environ['CONDA_DEFAULT_ENV']
