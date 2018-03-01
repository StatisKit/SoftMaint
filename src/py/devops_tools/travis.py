import os
import yaml
import json
import git
import requests
import time

from requests.exceptions import ConnectionError
from requests.auth import HTTPBasicAuth

from .system import SYSTEM
from .__version__ import __version__

from . import credential
from . import conda
from . import docker

STAGES = ['install',
          'before_script',
          'script',
          'after_success',
          'before_deploy',
          'deploy',
          'after_deploy',
          'after_script']

HEADERS = {'user-agent': 'TravisDevOpsClient/' + __version__,
           'accept':'application/vnd.travis-ci.2+json',
           'host':'api.travis-ci.org',
           'content-type': 'application/json'}

def retrieve(login=None, password=None):
    if password is None:
        password = os.environ.get('TRAVIS_TOKEN', None)
    login, password = credential.retrieve('travis.com',
                                          login="TOKEN",
                                          password=password)
    credential.__CACHE__['travis.com'] = dict(login = login,
                                              password = password,
                                              account = None)
    return login, password

def authenticate(token=None):
    if not token and not 'authorization' in HEADERS:
        login, password = credential.retrieve(host='github.com',
                                              stdin=False)
        github_auth = HTTPBasicAuth(login, password)
        github_url = "https://api.github.com/authorizations"
        github_data = dict(note = "DevOps Tools Client",
                           scopes = ["repo",
                                     "admin:org",
                                     "admin:public_key",
                                     "admin:repo_hook",
                                     "admin:org_hook",
                                     "gist",
                                     "notifications",
                                     "user",
                                     "delete_repo",
                                     "admin:gpg_key"])
        github_request = requests.post(github_url,
                                       auth=github_auth,
                                       data=json.dumps(github_data))
        if not github_request.ok:
            raise ConnectionError(github_request.text)
        else:
            github_request = github_request.json()
        travis_url = "https://api.travis-ci.org/auth/github"
        travis_data = dict(github_token = github_request["token"])
        travis_request = requests.post(travis_url,
                                       data=json.dumps(travis_data),
                                       headers=HEADERS)
        requests.delete(url=github_url + "/" + str(github_request["id"]),
                        auth=github_auth)
        if not travis_request.ok:
            raise ConnectionError(travis_request.text)
        else:
            travis_request = travis_request.json()
        token = travis_request["access_token"]
    if token:
        HEADERS['authorization'] = 'token ' + token

def _wait(sleep=.5):
    time.sleep(sleep)
    travis_url = "https://api.travis-ci.org/users"
    travis_request = requests.get(travis_url,
                                  headers=HEADERS)
    if not travis_request.ok:
        raise ConnectionError(travis_request.text)
    else:
        travis_request = travis_request.json()
    while travis_request["user"]["is_syncing"]:
        time.sleep(sleep)
        travis_request = requests.get(travis_url,
                                      headers=HEADERS)
        if not travis_request.ok:
            raise ConnectionError(travis_request.text)
        else:
            travis_request = travis_request.json()

def _sync(sleep=.5):
    _wait(sleep=sleep)
    travis_url = "https://api.travis-ci.org/users/sync"
    travis_request = requests.post(travis_url,
                                   headers=HEADERS)
    if not travis_request.ok:
        raise ConnectionError(travis_request.text)
    _wait(sleep=sleep)

def _fetch(repository):
    travis_url = "https://api.travis-ci.org/repos/" + repository["owner"]["login"] + "/" + repository["name"]
    travis_request = requests.get(travis_url,
                                  headers=HEADERS)
    if not travis_request.ok:
        raise ConnectionError(travis_request.text)
    else:
        travis_request = travis_request.json()
    return travis_request

def fetch(repository):
    authenticate()
    return _fetch(repository)
    
def _hook(repository, active=True):
    repository_id = _fetch(repository=repository)["repo"]["id"]
    travis_url = "https://api.travis-ci.org/hooks"
    travis_data = dict(hook = dict(id = repository_id, active=active))
    travis_request = requests.put(travis_url,
                                  data=json.dumps(travis_data),
                                  headers=HEADERS)
    if not travis_request.ok:
        raise ConnectionError(travis_request.text)
    else:
        travis_request = travis_request.json()

def _settings(repository, anaconda_label=None, anaconda_owner=None, docker_owner=None):
    repository_id = _fetch(repository=repository)["repo"]["id"]
    travis_url = "https://api.travis-ci.org/settings/env_vars"
    anaconda_login, anaconda_password = conda.retrieve()
    travis_datas = []
    if anaconda_login:
        travis_datas.append(dict(repository_id = repository_id,
                                 env_var = dict(name = "ANACONDA_LOGIN",
                                                value = anaconda_login,
                                                public = True)))
    if anaconda_password:
        travis_datas.append(dict(repository_id = repository_id,
                                 env_var = dict(name = "ANACONDA_PASSWORD",
                                                value = anaconda_password,
                                                public = False)))
    if anaconda_label:
        travis_datas.append(dict(repository_id = repository_id,
                                 env_var = dict(name = "ANACONDA_LABEL",
                                                value = anaconda_label,
                                                public = True)))
    if anaconda_login and anaconda_password:
        if not anaconda_owner:
            anaconda_owner = repository["owner"]["login"]
        travis_datas.append(dict(repository_id = repository_id,
                                 env_var = dict(name = "ANACONDA_OWNER",
                                                value = anaconda_owner,
                                                public = True)))
    docker_login, docker_password = docker.retrieve()
    if docker_login:
        travis_datas.append(dict(repository_id = repository_id,
                                 env_var = dict(name = "DOCKER_LOGIN",
                                                value = docker_login,
                                                public = True)))
    if docker_password:
        travis_datas.append(dict(repository_id = repository_id,
                                 env_var = dict(name = "DOCKER_PASSWORD",
                                                value = docker_password,
                                                public = False)))
    if docker_login and docker_password:
        if not docker_owner:
            docker_owner = repository["owner"]["login"]
        travis_datas.append(dict(repository_id = repository_id,
                                 env_var = dict(name = "DOCKER_OWNER",
                                                value = docker_owner,
                                                public = True)))
    for travis_data in travis_datas:
      travis_request = requests.post(travis_url,
                                    data=json.dumps(travis_data),
                                    headers=HEADERS)
      if not travis_request.ok:
          raise ConnectionError(travis_request.text)
      else:
          travis_request = travis_request.json()

def init(repository, sleep=.1, anaconda_owner=None, anaconda_label=None, docker_owner=None):
    authenticate()
    _sync(sleep=sleep)
    _hook(repository=repository, active=True)
    _sync(sleep=sleep)
    _settings(repository=repository,
             anaconda_owner=anaconda_owner,
             anaconda_label=anaconda_label,
             docker_owner=docker_owner)
    _sync(sleep=sleep)

def reset(repository, sleep=.1, anaconda_owner=None, anaconda_label=None, docker_owner=None):
    authenticate()
    _sync(sleep=sleep)
    _settings(repository=repository,
             anaconda_owner=anaconda_owner,
             anaconda_label=anaconda_label,
             docker_owner=docker_owner)
    _sync(sleep=sleep)

def deinit(repository, sleep=.1):
    authenticate()
    _sync(sleep=sleep)
    _hook(repository=repository, active=False)
    _sync(sleep=sleep)

def build(repository, conda_prefix, dry_run):
    pass
    # if SYSTEM in ['linux', 'osx']:
    #     if os.path.exists('travis.yml'):
    #         travis = 'travis.yml'
    #     elif os.path.exists('travis.yml'):
    #         travis = '.travis.yml'
    #     else:
    #         raise IOError('No travis.yml or .travis.yml found')
    #     try:
    #         repo = git.Repo('.')
    #         branch = repo.active_branch.name
    #     except:
    #         branch = 'master'
    #     with open(travis, 'r') as filehandler:
    #         travis = yaml.load(filehandler.read())
    #     if not SYSTEM in travis.get('os', [SYSTEM]):
    #         raise IOError("Travis CI configuration file is designed for a '" + SYSTEM + "' operating system")
    #     if deploy:
    #         anaconda_login, anaconda_password = conda.retrieve(login = anaconda_login, password = anaconda_password)
    #         if any([anaconda_login, anaconda_password]):
    #             while not anaconda_owner:
    #                 anaconda_owner = raw_input('Anaconda Cloud Upload Organization: ')
    #                 if not anaconda_owner:
    #                     warnings.warn('Invalid Organization...', UserWarning)
    #         if SYSTEM == 'linux':
    #             docker_login, docker_password = docker.retrieve(login = docker_login, password = docker_password)
    #             if any([docker_login, docker_password]):
    #                 while not docker_owner:
    #                     docker_owner = raw_input('Docker Hub Upload Organization: ')
    #                     if not docker_owner:
    #                         warnings.warn('Invalid Organization...', UserWarning)
    #     with open('travis_build.sh', 'w') as buildhandler:
    #         buildhandler.write('set -ve\n\n')
    #         buildhandler.write('export PATH=' + os.pathsep.join([path for path in os.environ['PATH'].split(os.pathsep) if not os.path.exists(os.path.join(path, 'conda'))]) + '\n\n')
    #         buildhandler.write('export CI=false\n')
    #         if conda_prefix:
    #             conda_prefix = os.path.expanduser(conda_prefix)
    #             conda_prefix = os.path.expandvars(conda_prefix)
    #             conda_prefix = os.path.abspath(conda_prefix)
    #             conda_existed = os.path.exists(conda_prefix)
    #             buildhandler.write('export CONDA_PREFIX=' + conda_prefix + '\n\n')
    #         else:
    #             conda_existed = False
    #         buildhandler.write('export TRAVIS_OS_NAME=' + SYSTEM + '\n')
    #         buildhandler.write('export TRAVIS_BRANCH=' + branch + '\n\n')
    #         if not deploy:
    #             buildhandler.write('export ANACONDA_DEPLOY=false\n')
    #         buildhandler.write('export ANACONDA_LOGIN=' + anaconda_login + '\n')
    #         buildhandler.write('export ANACONDA_PASSWORD=' + anaconda_password + '\n')
    #         buildhandler.write('export ANACONDA_OWNER=' + anaconda_owner + '\n')
    #         buildhandler.write('export ANACONDA_LABEL=' + anaconda_label + '\n\n')
    #         if SYSTEM == 'linux':
    #             if not deploy:
    #                 buildhandler.write('export DOCKER_DEPLOY=false\n')
    #             buildhandler.write('export DOCKER_LOGIN=' + docker_login + '\n')
    #             buildhandler.write('export DOCKER_PASSWORD=' + docker_password + '\n')
    #             buildhandler.write('export DOCKER_OWNER=' + docker_owner + '\n\n')
    #         exclude = set()
    #         for job in travis.get('matrix', {}).get('exclude', []):
    #             if SYSTEM == job.get('os', SYSTEM):
    #                 exclude.add(tuple(sorted(job.get('env', '').split())))
    #         for index, job in enumerate(travis.get('env')):
    #             if not tuple(sorted(job.split())) in exclude:
    #                 with open(os.path.join('travis_job_' + str(index) + '.sh'), 'w') as jobhandler:
    #                     jobhandler.write('set -ve\n\n')
    #                     jobhandler.writelines(['export ' + var + '\n' for var in job.split()])
    #                     jobhandler.write('\n')
    #                     for stage in STAGES:
    #                         if stage == 'deploy':
    #                             jobhandler.write(travis.get(stage, {}).get('script', {}) + '\n')
    #                         else:
    #                             jobhandler.write('\n'.join(travis.get(stage, [])) + '\n')
    #                     jobhandler.writelines('cd ..\n')
    #                     jobhandler.writelines('\nrm ' + os.path.join('travis_job_' + str(index) + '.sh') + '\n')
    #                     jobhandler.write('\nset -ve')
    #                 buildhandler.write('if [[ -f ' + 'travis_job_' + str(index) + '.sh ]]; then\n')
    #                 buildhandler.write('  bash ' + 'travis_job_' + str(index) + '.sh\n')
    #                 buildhandler.write('  rm -rf travis-ci\n')
    #                 buildhandler.write('fi\n')
    #         if deploy and not conda_existed:
    #             buildhandler.write('\nrm -rf ' + conda_prefix + '\n')                
    #         buildhandler.write('\nrm travis_build.sh\n')
    #         buildhandler.write('\nset +ve')
