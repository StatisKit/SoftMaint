import datetime
import six
import subprocess

if six.PY3:
    from subprocess import DEVNULL
else:
    DEVNULL = open(os.devnull, 'wb')

def git_describe_version(repository):
    try:
        if six.PY2:
            print(subprocess.check_output(['git', '-C', repository, 'describe', '--tags'], stderr=DEVNULL).splitlines()[0].split("-")[0].strip('v'))
        else:
            print(subprocess.check_output(['git', '-C', repository, 'describe', '--tags'], stderr=DEVNULL).splitlines()[0].decode().split("-")[0].strip('v'))
    except:
        print("0.1.0")

def git_describe_number(repository):
    try:
        if six.PY2:
            output = subprocess.check_output(['git', '-C', repository, 'describe', '--tags'], stderr=DEVNULL).splitlines()[0].split('-')
        else:
            output = subprocess.check_output(['git', '-C', repository, 'describe', '--tags'], stderr=DEVNULL).splitlines()[0].decode().split('-')
        if len(output) == 4:
            print(output[2])
        elif len(output) == 3:
            print(output[1]) 
        else:
            raise ValueError()
    except:
        try:
            if six.PY2:
                print(subprocess.check_output(['git', '-C', repository, 'rev-list', 'HEAD', '--count']).splitlines()[0])
            else:
                print(subprocess.check_output(['git', '-C', repository, 'rev-list', 'HEAD', '--count']).splitlines()[0].decode())
        except:
            print("0")

def datetime_describe_version(repository):
    now = datetime.datetime.now()
    print(str(now.year % 2000) + "." + str(now.month).rjust(2, '0')  + "." + str(now.day).rjust(2, '0'))

def datetime_describe_number(repository):
    if 'TRAVIS_BUILD_NUMBER' in os.environ:
        print(os.environ['TRAVIS_BUILD_NUMBER'])
    else:
        now = datetime.datetime.now()
        try:
            if PY2:
                print(subprocess.check_output(['git', '-C', repository, 'rev-list', 'HEAD', '--count', '--after="' + str(now.year) + '/' + str(now.month).rjust(2, '0') + '/' + str(now.day).rjust(2, '0') + ' 00:00:00"']).splitlines()[0])
            else:
                print(subprocess.check_output(['git', '-C', repository, 'rev-list', 'HEAD', '--count', '--after="' + str(now.year) + '/' + str(now.month).rjust(2, '0') + '/' + str(now.day).rjust(2, '0') + ' 00:00:00"']).splitlines()[0].decode())
        except:
            print(str(now.hour).rjust(2, '0'))