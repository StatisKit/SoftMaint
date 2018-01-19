from .login import login

def docker_login(username=None, password=None):
    return login('Docker Hub', username=username, password=password)
