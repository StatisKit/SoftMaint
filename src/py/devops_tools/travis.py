import os
import yaml
import git

from .conda import anaconda_login
from .docker import docker_login
from .system import SYSTEM

STAGES = ['install',
          'before_script',
          'script',
          'after_success',
          'before_deploy',
          'deploy',
          'after_deploy',
          'after_script']

def travis_scripts(anaconda_username='', anaconda_password='', anaconda_upload='', anaconda_label='release',
                   conda_prefix=None, deploy=True,
                   docker_username='', docker_password='', docker_upload=''):
    if SYSTEM in ['linux', 'osx']:
        if os.path.exists('travis.yml'):
            travis = 'travis.yml'
        elif os.path.exists('travis.yml'):
            travis = '.travis.yml'
        else:
            raise IOError('No travis.yml or .travis.yml found')
        try:
            repo = git.Repo('.')
            branch = repo.active_branch.name
        except:
            branch = 'master'
        with open(travis, 'r') as filehandler:
            travis = yaml.load(filehandler.read())
        if not SYSTEM in travis.get('os', [SYSTEM]):
            raise IOError("Travis CI configuration file is designed for a '" + SYSTEM + "' operating system")
        if deploy:
            anaconda_username, anaconda_password = anaconda_login(username = anaconda_username, password = anaconda_password)
            if any([anaconda_username, anaconda_password]):
                while not anaconda_upload:
                    anaconda_upload = raw_input('Anaconda Cloud Upload Organization: ')
                    if not anaconda_upload:
                        warnings.warn('Invalid Organization...', UserWarning)
            if SYSTEM == 'linux':
                docker_username, docker_password = docker_login(username = docker_username, password = docker_password)
                if any([docker_username, docker_password]):
                    while not docker_upload:
                        docker_upload = raw_input('Docker Hub Upload Organization: ')
                        if not docker_upload:
                            warnings.warn('Invalid Organization...', UserWarning)
        with open('travis_build.sh', 'w') as buildhandler:
            buildhandler.write('set -ve\n\n')
            buildhandler.write('export PATH=' + os.pathsep.join([path for path in os.environ['PATH'].split(os.pathsep) if not os.path.exists(os.path.join(path, 'conda'))]) + '\n\n')
            buildhandler.write('export CI=false\n')
            if conda_prefix:
                conda_prefix = os.path.expanduser(conda_prefix)
                conda_prefix = os.path.expandvars(conda_prefix)
                conda_prefix = os.path.abspath(conda_prefix)
                conda_existed = os.path.exists(conda_prefix)
                buildhandler.write('export CONDA_PREFIX=' + conda_prefix + '\n\n')
            else:
                conda_existed = False
            buildhandler.write('export TRAVIS_OS_NAME=' + SYSTEM + '\n')
            buildhandler.write('export TRAVIS_BRANCH=' + branch + '\n\n')
            if not deploy:
                buildhandler.write('export ANACONDA_DEPLOY=false\n')
            buildhandler.write('export ANACONDA_USERNAME=' + anaconda_username + '\n')
            buildhandler.write('export ANACONDA_PASSWORD=' + anaconda_password + '\n')
            buildhandler.write('export ANACONDA_UPLOAD=' + anaconda_upload + '\n')
            buildhandler.write('export ANACONDA_LABEL=' + anaconda_label + '\n\n')
            if SYSTEM == 'linux':
                if not deploy:
                    buildhandler.write('export DOCKER_DEPLOY=false\n')
                buildhandler.write('export DOCKER_USERNAME=' + docker_username + '\n')
                buildhandler.write('export DOCKER_PASSWORD=' + docker_password + '\n')
                buildhandler.write('export DOCKER_UPLOAD=' + docker_upload + '\n\n')
            exclude = set()
            for job in travis.get('matrix', {}).get('exclude', []):
                if SYSTEM == job.get('os', SYSTEM):
                    exclude.add(tuple(sorted(job.get('env', '').split())))
            for index, job in enumerate(travis.get('env')):
                if not tuple(sorted(job.split())) in exclude:
                    with open(os.path.join('travis_job_' + str(index) + '.sh'), 'w') as jobhandler:
                        jobhandler.write('set -ve\n\n')
                        jobhandler.writelines(['export ' + var + '\n' for var in job.split()])
                        jobhandler.write('\n')
                        for stage in STAGES:
                            if stage == 'deploy':
                                jobhandler.write(travis.get(stage, {}).get('script', {}) + '\n')
                            else:
                                jobhandler.write('\n'.join(travis.get(stage, [])) + '\n')
                        jobhandler.writelines('cd ..\n')
                        jobhandler.writelines('\nrm ' + os.path.join('travis_job_' + str(index) + '.sh') + '\n')
                        jobhandler.write('\nset -ve')
                    buildhandler.write('if [[ -f ' + 'travis_job_' + str(index) + '.sh ]]; then\n')
                    buildhandler.write('  bash ' + 'travis_job_' + str(index) + '.sh\n')
                    buildhandler.write('  rm -rf travis-ci\n')
                    buildhandler.write('fi\n')
            if deploy and not conda_existed:
                buildhandler.write('\nrm -rf ' + conda_prefix + '\n')                
            buildhandler.write('\nrm travis_build.sh\n')
            buildhandler.write('\nset +ve')
