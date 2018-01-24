import os
import yaml
import git

from .conda import anaconda_login
from .system import SYSTEM

STAGES = ['install',
          'before_build',
          'build_script',
          'after_build',
          'before_deploy',
          'deploy_script',
          'after_deploy',
          'on_succes',
          'on_failure']

def appveyor_scripts(anaconda_username=None, anaconda_password=None, anaconda_upload='', anaconda_label='release', with_log=False):
    if SYSTEM == 'win':
        if os.path.exists('appveyor.yml'):
            appveyor = 'appveyor.yml'
        elif os.path.exists('appveyor.yml'):
            appveyor = '.appveyor.yml'
        else:
            raise IOError('No appveyor.yml or .appveyor.yml found')
        try:
            repo = git.Repo('.')
            branch = repo.active_branch.name
        except:
            branch = 'master'
        with open(appveyor, 'r') as filehandler:
            appveyor = yaml.load(filehandler.read())
        if not SYSTEM in appveyor.get('os', [SYSTEM]):
            raise IOError("Travis CI configuration file is designed for a '" + SYSTEM + "' operating system")
        anaconda_username, anaconda_password = anaconda_login(username = anaconda_username, password = anaconda_password)
        if any([anaconda_username, anaconda_password]):
            while not anaconda_upload:
                anaconda_upload = raw_input('Anaconda Cloud Upload Organization: ')
                if not anaconda_upload:
                    warnings.warn('Invalid Organization...', UserWarning)
        with open('appveyor_build.bat', 'w') as buildhandler:
            buildhandler.write('echo ON\n\n')
            buildhandler.write('set CI=false\n')
            buildhandler.write('set APPVEYOR_REPO_BRANCH=' + branch + '\n\n')
            buildhandler.write('set ANACONDA_USERNAME=' + anaconda_username + '\n')
            buildhandler.write('set ANACONDA_PASSWORD=' + anaconda_password + '\n')
            buildhandler.write('set ANACONDA_UPLOAD=' + anaconda_upload + '\n')
            buildhandler.write('set ANACONDA_LABEL=' + anaconda_label + '\n\n')
            exclude = set()
            # for job in appveyor.get('matrix', {}).get('exclude', []):
            #     if not SYSTEM == job.get('os', SYSTEM):
            #         exclude.add(set(job.get('env', [])))
            for index, job in enumerate(appveyor.get('environment').get('matrix')):
                if not tuple(sorted(job)) in exclude:
                    with open(os.path.join('appveyor_job_' + str(index) + '.bat'), 'w') as jobhandler:
                        jobhandler.writelines(['set ' + str(key) + '=' + str(value) + '\n' for key, value in job.items()])
                        for stage in STAGES:
                            jobhandler.write('\nif errorlevel 1 exit 1\n'.join(appveyor.get(stage, [])) + '\n')
                        jobhandler.writelines('del ' + os.path.join('appveyor_job_' + str(index) + '.bat') + '\nif errorlevel 1 exit 1')
                    buildhandler.write('if exist ' + 'appveyor_job_' + str(index) + '.bat (\n')
                    buildhandler.write('  start /wait ' + 'appveyor_job_' + str(index) + '.bat ' + with_log * (' ^1^> log_' + str(index) + ' ^2^>^&^1\n'))
                    buildhandler.write('  if errorlevel 1 exit 1\n')
                    buildhandler.write(')\n')
            buildhandler.write('\ndel appveyor_build.bat\nif errorlevel 1 exit 1\n')
            buildhandler.write('\necho OFF')
