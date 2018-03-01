import os
import yaml
import json
import git
import requests

from requests.exceptions import ConnectionError

from .system import SYSTEM
from .__version__ import __version__

from . import credential
from . import conda
from . import docker

STAGES = ['install',
          'before_build',
          'build_script',
          'after_build',
          'before_deploy',
          'deploy_script',
          'after_deploy',
          'on_success',
          'on_finish']

HEADERS = {'user-agent': 'AppVeyorDevOpsClient/' + __version__,
           'accept':'application/json',
           'content-type': 'application/json'}


def retrieve(login=None, password=None):
    if password is None:
        password = os.environ.get('APPVEYOR_TOKEN', None)
    login, password = credential.retrieve('appveyor.com',
                                          login="TOKEN",
                                          password=password)
    credential.__CACHE__['appveyor.com'] = dict(login = login,
                                                password = password,
                                                account = None)
    return login, password

def authenticate(token=None):
    if not token and not 'authorization' in HEADERS:
        login, token = retrieve(login=None, password=token)
    if token:
        HEADERS['authorization'] = 'Bearer ' + token

def _fetch(repository):
    appveyor_url = "https://ci.appveyor.com/api/projects"
    appveyor_request = requests.get(appveyor_url,
                                    headers=HEADERS)
    if not appveyor_request.ok:
        raise ConnectionError(appveyor_request.text)
    else:
        appveyor_request = appveyor_request.json()
    appveyor_data = None
    for item in appveyor_request:
        if item["repositoryName"] == repository["owner"]["login"] + "/" + repository["name"]:
            appveyor_data = item
            break
    if not appveyor_data:
        raise ConnectionError("Repository not initialized on AppVeyor")
    return appveyor_data

def fetch(repository):
    authenticate()
    return _fetch(repository)

def _settings(repository, anaconda_owner=None, anaconda_label=None):
    appveyor_data = _fetch(repository)
    appveyor_url = "https://ci.appveyor.com/api/projects/" + appveyor_data["accountName"] + "/" + appveyor_data["slug"] + "/settings"
    appveyor_request = requests.get(appveyor_url,
                                    headers=HEADERS)
    if not appveyor_request.ok:
        raise ConnectionError(appveyor_request.text)
    else:
        appveyor_request = appveyor_request.json()
    appveyor_url = "https://ci.appveyor.com/api/projects"
    appveyor_data = appveyor_request["settings"]
    appveyor_data["name"] = appveyor_data["repositoryName"]
    appveyor_data["slug"] = appveyor_data["repositoryName"]
    appveyor_subdata = appveyor_data["configuration"]["environmentVariables"]
    anaconda_login, anaconda_password = conda.retrieve()
    if anaconda_login:
        appveyor_subdata.append(dict(name = "ANACONDA_LOGIN",
                                     value = dict(value = anaconda_login,
                                                  isEncrypted = False)))
    if anaconda_password:
        appveyor_subdata.append(dict(name = "ANACONDA_PASSWORD",
                                     value = dict(value = anaconda_password,
                                                  isEncrypted = True)))
    if anaconda_label:
        appveyor_subdata.append(dict(name = "ANACONDA_LABEL",
                                     value = dict(value = anaconda_label,
                                                  isEncrypted = False)))
    if anaconda_login and anaconda_password:
        if not anaconda_owner:
            anaconda_owner = repository["owner"]["login"]
        appveyor_subdata.append(dict(name = "ANACONDA_OWNER",
                                     value = dict(value = anaconda_owner,
                                                  isEncrypted = False)))
    appveyor_data["configuration"]["environmentVariables"] = appveyor_subdata
    appveyor_request = requests.put(appveyor_url,
                                    data=json.dumps(appveyor_data),
                                    headers=HEADERS)
    if not appveyor_request.ok:
        raise ConnectionError(appveyor_request.text)

def init(repository, anaconda_owner=None, anaconda_label=None):
    authenticate()
    try:
        _fetch(repository)
    except:
        pass
    else:
        raise ConnectionError("Repository already initialized on AppVeyor")
    appveyor_url = "https://ci.appveyor.com/api/projects"
    appveyor_data = dict(repositoryProvider = "gitHub",
                         repositoryName = repository["owner"]["login"] + "/" + repository["name"])
    appveyor_request = requests.post(appveyor_url,
                                     data=json.dumps(appveyor_data),
                                     headers=HEADERS)
    if not appveyor_request.ok:
        raise ConnectionError(appveyor_request.text)
    else:
        appveyor_request = appveyor_request.json()
    _settings(repository=repository,
              anaconda_owner=anaconda_owner,
              anaconda_label=anaconda_label)

def reset(repository, anaconda_owner=None, anaconda_label=None):
    authenticate()
    _settings(repository=repository,
              anaconda_owner=anaconda_owner,
              anaconda_label=anaconda_label)

def deinit(repository):
    authenticate()
    appveyor_data = _fetch(repository)
    if not appveyor_data:
        raise ConnectionError("Repository not initialized on AppVeyor")
    appveyor_url = "https://ci.appveyor.com/api/projects/" + appveyor_data["accountName"] + "/" + appveyor_data["slug"]
    appveyor_request = requests.delete(appveyor_url,
                                       headers=HEADERS)
    if not appveyor_request.ok:
        raise ConnectionError(appveyor_request.text)

def build(repository, conda_prefix, dry_run):
    pass
    # if SYSTEM == 'win':
    #     if os.path.exists('appveyor.yml'):
    #         appveyor = 'appveyor.yml'
    #     elif os.path.exists('appveyor.yml'):
    #         appveyor = '.appveyor.yml'
    #     else:
    #         raise IOError('No appveyor.yml or .appveyor.yml found')
    #     try:
    #         repo = git.Repo('.')
    #         branch = repo.active_branch.name
    #     except:
    #         branch = 'master'
    #     with open(appveyor, 'r') as filehandler:
    #         appveyor = yaml.load(filehandler.read())
    #     if not SYSTEM in appveyor.get('os', [SYSTEM]):
    #         raise IOError("AppVeyor CI configuration file is designed for a '" + SYSTEM + "' operating system")
    #     if deploy:
    #         anaconda_login, anaconda_password = conda._credential(login = anaconda_login, password = anaconda_password)
    #         if any([anaconda_login, anaconda_password]):
    #             while not anaconda_owner:
    #                 anaconda_owner = raw_input('Anaconda Cloud Upload Organization: ')
    #                 if not anaconda_owner:
    #                     warnings.warn('Invalid Organization...', UserWarning)
    #     with open('appveyor_build.bat', 'w') as buildhandler:
    #         buildhandler.write('echo ON\n\n')
    #         buildhandler.write('export PATH=' + os.pathsep.join([path for path in os.environ['PATH'].split(os.pathsep) if not(os.path.exists(os.path.join(path, 'conda.exe')) or os.path.exists(os.path.join(path, 'conda.bat')))]) + '\n\n')
    #         buildhandler.write('set CI=false\n')
    #         if conda_prefix:
    #             conda_prefix = os.path.expanduser(conda_prefix)
    #             conda_prefix = os.path.expandvars(conda_prefix)
    #             conda_prefix = os.path.abspath(conda_prefix)
    #             conda_existed = os.path.exists(conda_prefix)
    #             buildhandler.write('set CONDA_PREFIX=' + conda_prefix + '\n\n')
    #         else:
    #             conda_existed = False
    #         buildhandler.write('set APPVEYOR_BUILD_FOLDER=' + os.path.abspath('.') + '\n')
    #         buildhandler.write('set APPVEYOR_REPO_BRANCH=' + branch + '\n\n')
    #         buildhandler.write('set ANACONDA_USERNAME=' + anaconda_login + '\n')
    #         buildhandler.write('set ANACONDA_PASSWORD=' + anaconda_password + '\n')
    #         buildhandler.write('set ANACONDA_OWNER=' + anaconda_owner + '\n')
    #         buildhandler.write('set ANACONDA_LABEL=' + anaconda_label + '\n\n')
    #         exclude = set()
    #         # for job in appveyor.get('matrix', {}).get('exclude', []):
    #         #     if not SYSTEM == job.get('os', SYSTEM):
    #         #         exclude.add(set(job.get('env', [])))
    #         for index, job in enumerate(appveyor.get('environment').get('matrix')):
    #             if not tuple(sorted(job)) in exclude:
    #                 with open(os.path.join('appveyor_job_' + str(index) + '.bat'), 'w') as jobhandler:
    #                     jobhandler.write('echo ON\n\n')
    #                     jobhandler.writelines(['set ' + str(key) + '=' + str(value) + '\n' for key, value in job.items()])
    #                     for stage in STAGES:
    #                         jobhandler.write('\nif errorlevel 1 exit /b 1\n'.join(appveyor.get(stage, [])) + '\n')
    #                     jobhandler.write('cd ..\n')
    #                     jobhandler.write('\necho OFF\n')
    #                     jobhandler.write('\ndel appveyor_job_' + str(index) + '.bat & exit 0')
    #                 buildhandler.write('if exist ' + 'appveyor_job_' + str(index) + '.bat (\n')
    #                 buildhandler.write('  start /wait ' + 'appveyor_job_' + str(index) + '.bat\n')
    #                 buildhandler.write('  if errorlevel 1 exit /b 1\n')
    #                 buildhandler.write('  rmdir appveyor-ci /S /q\n')
    #                 buildhandler.write('  if errorlevel 1 exit /b 1\n')
    #                 buildhandler.write(')\n')
    #         if deploy and not conda_existed:
    #             buildhandler.write('\nrmdir ' + conda_prefix + '/S /Q\n')  
    #         buildhandler.write('\necho OFF\n')
    #         buildhandler.write('\ndel appveyor_build.bat & exit 0')