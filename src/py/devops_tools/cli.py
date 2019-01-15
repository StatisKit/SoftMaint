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
import subprocess
import six
import datetime

from .walkfiles import main as walkfiles
from .system import SYSTEM

from . import config
from . import credential
from . import notice
from . import cpu_count
from . import sublime_text
from . import conda
from . import github
from . import travis
from . import appveyor

if six.PY3:
    from subprocess import DEVNULL
else:
    import os
    DEVNULL = open(os.devnull, 'wb')

def main_devops():

    parser = argparse.ArgumentParser()
    parser.add_argument('--set-netrc-update',
                        dest = 'netrc_update',
                        action = 'store_true',
                        help  = 'Store credentials after each command executed to register credentials used')
    parser.set_defaults(netrc_update = None)
    args = parser.parse_args()
    config.set_netrc_update(update=args.netrc_update)

def main_notice():

    parser = argparse.ArgumentParser()
    parser.add_argument('directory',
                        help  = 'The directory in which files need to include NOTICE as a license header',
                        nargs = '?',
                        default = '.')
    parser.add_argument('filename',
                        help  = 'The filename containing the content of include as files\' license header',
                        nargs = '?',
                        default = 'NOTICE')
    parser.add_argument('--check',
                        dest = 'check',
                        action = 'store_true',
                        help = "")
    parser.set_defaults(check = False)
    args = parser.parse_args()

    filepath = Path(args.directory)/args.filename
    if not filepath.exists():
        raise ValueError("'filename' argument is invalid")
    with open(filepath, 'r') as filehandler:
        filecontent = filehandler.read()
    for filepath in walkfiles(args.directory):
        content = notice.replace(filepath, filecontent)
        if args.check:
            with open(filepath, "r") as filehandler:
                if not content == filehandler.read():
                    raise Exception("NOTICE file has changed or was not included in file '" + str(filepath) + "'")
        with open(filepath, "w") as filehandler:
            filehandler.write(content)

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
                        default = os.path.join(conda.current_prefix(), 'etc', 'conda', 'activate.d', 'activate-cpu_count.' + ext))
    parser.add_argument('--deactivate',
                        dest='deactivate',
                        nargs='?',
                        help  = 'The file in which the definition of CPU_COUNT environment variable will be unsetted',
                        default = os.path.join(conda.current_prefix(), 'etc', 'conda', 'deactivate.d', 'deactivate-cpu_count.' + ext))
    parser.add_argument('--number',
                        dest='number',
                        help  = 'The number of CPUs to use with builds',
                        nargs='?',
                        type = int,
                        choices = cpu_count.choices(),
                        default = cpu_count.default())
    args = parser.parse_args()

    with open(args.activate, 'w') as filehandler:
        filehandler.write(cpu_count.activate(args.number))

    with open(args.deactivate, 'w') as filehandler:
        filehandler.write(cpu_count.deactivate())

def main_github():

    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers(title='subcommands',
                                       help='additional help')

    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument('repository',
                                nargs='?',
                                default='.',
                                help  = 'The repository to consider')

    specific_parser = argparse.ArgumentParser(add_help=False)
    specific_parser.add_argument('--issue',
                                 dest = 'number',
                                 help = "The issue number")

    issues_parser = subparsers.add_parser('issues', parents=[parent_parser])
    issues_parser.add_argument('--browser',
                               dest = 'browser',
                               action = 'store_true',
                               help = "Use your Web browser to show results")
    issues_parser.set_defaults(browser = False)
    issues_parser.add_argument('--assigned',
                               dest = 'assigned',
                               action = 'store_true',
                               help = "Consider issues that has been assigned to you")
    issues_parser.set_defaults(assigned = False)
    issues_parser.set_defaults(func = github.issues)

    issue_parser = subparsers.add_parser('issue', parents=[parent_parser])
    issue_parser.add_argument('number',
                               nargs='?',
                               default = None,
                               help = "The issue number")
    issue_parser.add_argument('--browser',
                              dest = 'browser',
                              action = 'store_true',
                              help = "Use your Web browser to show results")
    issue_parser.set_defaults(browser = False)
    issue_parser.set_defaults(func = github.issue)

    hotfix_parser = subparsers.add_parser('hotfix', parents=[parent_parser, specific_parser])
    hotfix_parser.add_argument('--remote',
                               nargs='?',
                               dest = 'remote',
                               default = 'upstream',
                               choices = ["upstream", "origin"],
                               help = "The remote url to use for branching")
    hotfix_parser.set_defaults(func = github.hotfix)

    feature_parser = subparsers.add_parser('feature', parents=[parent_parser, specific_parser])
    feature_parser.set_defaults(func = github.feature)

    start_parser = subparsers.add_parser('start', parents=[parent_parser])
    start_parser.add_argument('--branch',
                              nargs='?',
                              dest = 'branch',
                              default = None,
                              help = "The branch to checkout")
    start_parser.set_defaults(func = github.start)

    end_parser = subparsers.add_parser('end', parents=[parent_parser])
    end_parser.add_argument('--suggest',
                            dest = 'suggest',
                            action = 'store_true',
                            help = "Suggest repository modifications")
    end_parser.set_defaults(suggest = False)
    end_parser.set_defaults(func = github.end)


    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument('name',
                                help  = 'The name of the repository to consider')

    owner_parser = argparse.ArgumentParser(add_help=False)
    owner_parser.add_argument('--owner',
                              dest = 'owner',
                              default = None,
                              help = "The owner of the repository")

    parser_init = subparsers.add_parser('init', parents=[parent_parser, owner_parser])
    parser_init.add_argument('--description',
                              dest='description',
                              default=None,
                              help  = 'The repository description')
    parser_init.add_argument('--homepage',
                              dest='homepage',
                              default=None,
                              help  = 'The repository homepage')
    parser_init.add_argument('--private',
                              dest = 'private',
                              action = 'store_true',
                              help = "Set the repository as a private one")
    parser_init.set_defaults(private = False)
    parser_init.add_argument('--no-issues',
                              dest = 'has_issues',
                              action = 'store_false',
                              help = "Do not activate issues on this repository")
    parser_init.set_defaults(has_issues = True)
    parser_init.add_argument('--no-projects',
                              dest = 'has_projects',
                              action = 'store_false',
                              help = "Do not activate projects on this repository")
    parser_init.set_defaults(has_projects = True)
    parser_init.add_argument('--wiki',
                              dest = 'has_wiki',
                              action = 'store_true',
                              help = "Activate the wiki on this repository")
    parser_init.set_defaults(has_wiki = False)
    parser_init.add_argument('--license',
                              dest = 'license',
                              choices = github.LICENSES,
                              help = "The license of this repository")
    parser_init.set_defaults(func = github.init)

    parser_deinit = subparsers.add_parser('deinit', parents=[parent_parser, owner_parser])
    parser_deinit.set_defaults(func = github.deinit)

    parser_clone = subparsers.add_parser('clone', parents=[parent_parser, owner_parser])
    parser_clone.add_argument('--to-path',
                              dest = 'to_path',
                              nargs="?",
                              default=None,
                              help = "The path to clone into")
    parser_clone.add_argument('--no-recursive',
                              dest = 'recursive',
                              action = 'store_false',
                              help = "Do not initialize submodules")
    parser_clone.set_defaults(recursive = True)
    parser_clone.set_defaults(func = github.clone)

    parser_fork = subparsers.add_parser('fork', parents=[parent_parser])
    parser_fork.add_argument('--owner',
                              dest='owner',
                              help = "The owner of the repository")
    parser_fork.set_defaults(func = github.fork)

    args = parser.parse_args()
    kwargs = vars(args)
    func = kwargs.pop("func")
    func(**kwargs)

def main_travis_ci():

    parser = argparse.ArgumentParser()

    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument('repository',
                        help  = 'A local or web-based repository to consider',
                        nargs = '?',
                        default = '.')

    deploy_parser = argparse.ArgumentParser(add_help=False)
    deploy_parser.add_argument('--anaconda-owner',
                        dest='anaconda_owner',
                        nargs='?',
                        help  = 'Anaconda Cloud account to upload to',
                        default = '')
    deploy_parser.add_argument('--anaconda-label',
                        dest='anaconda_label',
                        nargs='?',
                        help  = 'Anaconda Cloud account\'s label to set when uploading',
                        default = 'release')
    deploy_parser.add_argument('--docker-owner',
                               dest='docker_owner',
                               nargs='?',
                               help  = 'Docker Hub account to upload to',
                               default = '')

    subparsers = parser.add_subparsers(title='subcommands',
                                       help='additional help')

    parser_init = subparsers.add_parser('init', parents=[parent_parser, deploy_parser])
    parser_init.set_defaults(func = travis.init)

    parser_reset = subparsers.add_parser('reset', parents=[parent_parser, deploy_parser])
    parser_reset.set_defaults(func = travis.reset)

    parser_deinit = subparsers.add_parser('deinit', parents=[parent_parser])
    parser_deinit.set_defaults(func = travis.deinit)

    parser_build = subparsers.add_parser('build', parents=[parent_parser])
    parser_build.add_argument('--conda-prefix',
                              dest='conda_prefix',
                              help  = 'The directory in which Conda will be installed',
                              nargs = '?',
                              default = os.path.join(os.environ['HOME'], 'miniconda'))
    parser_build.add_argument('--dry-run',
                              dest = 'dry_run',
                              action = 'store_true',
                              help = "Only write script files")
    parser_build.set_defaults(dry_run = False)
    parser_build.set_defaults(func = travis.build)

    args = parser.parse_args()
    args.repository = github.fetch(args.repository)
    kwargs = vars(args)
    func = kwargs.pop("func")
    func(**kwargs)

def main_appveyor_ci():

    parser = argparse.ArgumentParser()

    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument('repository',
                        help  = 'A local or web-based repository to consider',
                        nargs = '?',
                        default = '.')

    deploy_parser = argparse.ArgumentParser(add_help=False)
    deploy_parser.add_argument('--anaconda-owner',
                        dest='anaconda_owner',
                        nargs='?',
                        help  = 'Anaconda Cloud account to upload to',
                        default = '')
    deploy_parser.add_argument('--anaconda-label',
                        dest='anaconda_label',
                        nargs='?',
                        help  = 'Anaconda Cloud account\'s label to set when uploading',
                        default = 'release')

    subparsers = parser.add_subparsers(title='subcommands',
                                       help='additional help')

    parser_init = subparsers.add_parser('init', parents=[parent_parser, deploy_parser])
    parser_init.set_defaults(func = appveyor.init)

    parser_reset = subparsers.add_parser('reset', parents=[parent_parser, deploy_parser])
    parser_reset.set_defaults(func = appveyor.reset)

    parser_deinit = subparsers.add_parser('deinit', parents=[parent_parser])
    parser_deinit.set_defaults(func = appveyor.deinit)

    parser_build = subparsers.add_parser('build', parents=[parent_parser])
    parser_build.add_argument('--conda-prefix',
                              dest='conda_prefix',
                              help  = 'The directory in which Conda will be installed',
                              nargs = '?',
                              default = os.path.join(os.environ['HOME'], 'miniconda'))
    parser_build.add_argument('--dry-run',
                              dest = 'dry_run',
                              action = 'store_true',
                              help = "Only write script files")
    parser_build.set_defaults(dry_run = False)
    parser_build.set_defaults(func = appveyor.build)

    args = parser.parse_args()
    args.repository = github.fetch(args.repository)
    kwargs = vars(args)
    func = kwargs.pop("func")
    func(**kwargs)

def main_git_describe_version():
    try:
        if six.PY2:
            print(subprocess.check_output(['git', 'describe', '--tags'], stderr=DEVNULL).splitlines()[0].split("-")[0].strip('v'))
        else:
            print(subprocess.check_output(['git', 'describe', '--tags'], stderr=DEVNULL).splitlines()[0].decode().split("-")[0].strip('v'))
    except:
        print("0.1.0")

def main_git_describe_number():
    try:
        if six.PY2:
            print(subprocess.check_output(['git', 'describe', '--tags'], stderr=DEVNULL).splitlines()[0].split("-")[1])
        else:
            print(subprocess.check_output(['git', 'describe', '--tags'], stderr=DEVNULL).splitlines()[0].decode().split("-")[1])
    except:
        try:
            if six.PY2:
                print(subprocess.check_output(['git', 'rev-list', 'HEAD', '--count'], stderr=DEVNULL).splitlines()[0])
            else:
                print(subprocess.check_output(['git', 'rev-list', 'HEAD', '--count'], stderr=DEVNULL).splitlines()[0].decode())
        except:
            print("0")

def main_datetime_describe_version():
    now = datetime.datetime.now()
    print(str(now.year % 2000) + "." + str(now.month).rjust(2, '0')  + "." + str(now.day).rjust(2, '0'))

def main_datetime_describe_number():
    if 'TRAVIS_BUILD_NUMBER':
        print(os.environ['TRAVIS_BUILD_NUMBER'])
    else:
        now = datetime.datetime.now()
        print(now.hour)