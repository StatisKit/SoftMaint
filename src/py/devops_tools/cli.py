## Copyright [2017] UMR MISTEA INRA, UMR LEPSE INRA, UMR AGAP CIRAD,     ##
##                  EPI Virtual Plants Inria                             ##
##                                                                       ##
## This file is part of the StatisKit project. More information can be   ##
## found at                                                              ##
##                                                                       ##
##     http://statiskit.rtfd.io                                          ##
##                                                                       ##
## The Apache Software Foundation (ASF) licenses this file to you under  ##
## the Apache License, Version 2.0 (the "License"); you may not use this ##
## file except in compliance with the License. You should have received  ##
## a copy of the Apache License, Version 2.0 along with this file; see   ##
## the file LICENSE. If not, you may obtain a copy of the License at     ##
##                                                                       ##
##     http://www.apache.org/licenses/LICENSE-2.0                        ##
##                                                                       ##
## Unless required by applicable law or agreed to in writing, software   ##
## distributed under the License is distributed on an "AS IS" BASIS,     ##
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or       ##
## mplied. See the License for the specific language governing           ##
## permissions and limitations under the License.                        ##

from path import Path
import argparse
import os

from .walkfiles import main as walkfiles
from .notice import replace_notice
from .md5sum import compute_md5sum
from .cpu_count import get_range_cpu_count, get_default_cpu_count, activate_cpu_count, deactivate_cpu_count
from .system import SYSTEM
from .sublime_text import config_paths, BUILD_TARGET, BUILD_SYSTEM
from .conda import get_current_prefix, get_default_prefix, get_current_environment
from .travis import travis_scripts
from .appveyor import appveyor_scripts

def main_notice():

    parser = argparse.ArgumentParser()
    parser.add_argument('directory',
                        help  = 'The directory in which files need to include NOTICE as a license header',
                        nargs = '?',
                        default = '.')
    parser.add_argument('notice',
                        help  = 'The file containing the content of include as files\' license header',
                        nargs = '?',
                        default = 'NOTICE')
    parser.add_argument('--check',
                        dest = 'check',
                        action = 'store_true',
                        help = "")
    parser.set_defaults(check = False)
    args = parser.parse_args()

    notice = Path(args.directory)/args.notice
    if not notice.exists():
        raise ValueError("'notice' argument is invalid")
    with open(notice, 'r') as filehandler:
        notice = filehandler.read()
    for filepath in walkfiles(args.directory):
        content = replace_notice(filepath, notice)
        if args.check:
            with open(filepath, "r") as filehandler:
                if not content == filehandler.read():
                    raise Exception("NOTICE file has changed or was not included in file '" + str(filepath) + "'")
        with open(filepath, "w") as filehandler:
            filehandler.write(content)

def main_md5sum():

    parser = argparse.ArgumentParser()
    parser.add_argument('directory',
                        help  = 'The directory in which files need to include NOTICE as a license header',
                        nargs = '?',
                        default = '.')
    args = parser.parse_args()
    print(compute_md5sum(args.directory))

def main_cpu_count():

    if SYSTEM == 'win':
        ext = 'bat'
    else:
        ext = 'sh'

    parser = argparse.ArgumentParser()
    parser.add_argument('--activate',
                        dest='activate',
                        nargs='?',
                        help  = 'The file in which the definition of CPU_COUNT environment variable will be setted',
                        default = os.path.join(get_current_prefix(), 'etc', 'conda', 'activate.d', 'activate-cpu_count.' + ext))
    parser.add_argument('--deactivate',
                        dest='deactivate',
                        nargs='?',
                        help  = 'The file in which the definition of CPU_COUNT environment variable will be unsetted',
                        default = os.path.join(get_current_prefix(), 'etc', 'conda', 'deactivate.d', 'deactivate-cpu_count.' + ext))
    parser.add_argument('--cpu-count',
                        dest='cpu_count',
                        help  = 'The number of CPUs to use with builds',
                        nargs='?',
                        type = int,
                        choices = get_range_cpu_count(),
                        default = get_default_cpu_count())
    args = parser.parse_args()

    with open(args.activate, 'w') as filehandler:
        filehandler.write(activate_cpu_count(args.cpu_count))

    with open(args.deactivate, 'w') as filehandler:
        filehandler.write(deactivate_cpu_count())

def main_sublime_text():

    configs = config_paths()
    for config in configs:
        directory = os.path.join(config, 'Packages', 'StatisKit')
        if not os.path.exists(directory):
            os.makedirs(directory)
        with open(os.path.join(directory, 'SCons.sublime-build'), 'w') as filehandler:
            filehandler.write(BUILD_SYSTEM.replace('{{ prefix }}', get_current_prefix()).replace('{{ environment }}', get_current_environment()))
        with open(os.path.join(directory, 'scons.py'), 'w') as filehandler:
            filehandler.write(BUILD_TARGET)

def main_travis_ci():

    parser = argparse.ArgumentParser()

    parser.add_argument('--dry-run',
                        dest = 'dry_run',
                        action = 'store_true',
                        help = "Only write script files")
    parser.set_defaults(dry_run = False)
    parser.add_argument('--anaconda-username',
                        dest='anaconda_username',
                        nargs='?',
                        help  = 'Anaconda Cloud Username',
                        default = '')
    parser.add_argument('--anaconda-password',
                        dest='anaconda_password',
                        nargs='?',
                        help  = 'Anaconda Cloud Password',
                        default = '')
    parser.add_argument('--anaconda-upload',
                        dest='anaconda_upload',
                        nargs='?',
                        help  = 'Anaconda Cloud Organization',
                        default = '')
    parser.add_argument('--anaconda-label',
                        dest='anaconda_label',
                        nargs='?',
                        help  = 'Anaconda Cloud Organization\'s Label',
                        default = 'release')
    parser.add_argument('--conda-prefix',
                        dest='conda_prefix',
                        help  = 'The directory in which Conda will be installed',
                        nargs = '?',
                        default = os.path.join(os.environ['HOME'], 'miniconda'))
    parser.add_argument('--no-deploy',
                        dest = 'deploy',
                        action = 'store_false',
                        help = "Release locally")
    parser.set_defaults(deploy = True)
    if SYSTEM == 'linux':
        parser.add_argument('--docker-username',
                    dest='docker_username',
                    nargs='?',
                    help  = 'Docker Hub Username',
                    default = '')
        parser.add_argument('--docker-password',
                            dest='docker_password',
                            nargs='?',
                            help  = 'Docker Hub Password',
                            default = '')
        parser.add_argument('--docker-upload',
                            dest='docker_upload',
                            nargs='?',
                            help  = 'Docker Hub Organization',
                            default = '')

    args = parser.parse_args()

    if SYSTEM == 'linux':
        kwargs = dict(docker_username=args.docker_username,
                      docker_password=args.docker_password,
                      docker_upload=args.docker_upload)
    else:
        kwargs = dict()

    travis_scripts(anaconda_username=args.anaconda_username,
                   anaconda_password=args.anaconda_password,
                   anaconda_upload=args.anaconda_upload,
                   anaconda_label=args.anaconda_label,
                   conda_prefix=args.conda_prefix,
                   deploy=args.deploy,
                   **kwargs)

    if not args.dry_run:
        os.system('bash travis_build.sh')
        
def main_appveyor_ci():

    parser = argparse.ArgumentParser()

    parser.add_argument('--dry-run',
                        dest = 'dry_run',
                        action = 'store_true',
                        help = "Only write script files")
    parser.set_defaults(dry_run = False)
    parser.add_argument('--anaconda-username',
                        dest='anaconda_username',
                        nargs='?',
                        help  = 'Anaconda Cloud Username',
                        default = '')
    parser.add_argument('--anaconda-password',
                        dest='anaconda_password',
                        nargs='?',
                        help  = 'Anaconda Cloud Password',
                        default = '')
    parser.add_argument('--anaconda-upload',
                        dest='anaconda_upload',
                        nargs='?',
                        help  = 'Anaconda Cloud Organization',
                        default = '')
    parser.add_argument('--anaconda-label',
                        dest='anaconda_label',
                        nargs='?',
                        help  = 'Anaconda Cloud Organization\'s Label',
                        default = 'release')
    parser.add_argument('--conda-prefix',
                        dest='conda_prefix',
                        help  = 'The directory in which Conda will be installed',
                        nargs = '?',
                        default = os.path.join(os.environ['HOMEDRIVE'], 'miniconda'))
    parser.add_argument('--no-deploy',
                        dest = 'deploy',
                        action = 'store_false',
                        help = "Release locally")
    args = parser.parse_args()

    appveyor_scripts(anaconda_username=args.anaconda_username,
                     anaconda_password=args.anaconda_password,
                     anaconda_upload=args.anaconda_upload,
                     anaconda_label=args.anaconda_label,
                     conda_prefix=args.conda_prefix,
                     deploy=args.deploy,)


    if not args.dry_run:
        os.system('start /wait appveyor_build.bat')