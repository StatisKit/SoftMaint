from . import credential

def retrieve(login=None, password=None):
    login, password = credential.retrieve('hub.docker.com',
                                          login=login,
                                          password=password)
    credential.__CACHE__['hub.docker.com'] = dict(login = login,
                                                  password = password,
                                                  account = None)
    return login, password
