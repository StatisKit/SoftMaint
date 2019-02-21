import os
import requests
import subprocess

from requests.exceptions import ConnectionError

from .conda import retrieve

HEADERS = {'accept':'application/json',
           'content-type': 'application/json'}

def download(anaconda_owner=None, anaconda_label='main', force=True):
    anaconda_login, anaconda_password = retrieve()
    if anaconda_login and anaconda_password:
        if not anaconda_owner:
            anaconda_owner = repository["owner"]["login"]
    anaconda_url = "https://api.anaconda.org/packages/" + anaconda_owner
    anaconda_packages_request = requests.get(anaconda_url,
                                             headers=HEADERS)
    if not anaconda_packages_request.ok:
        raise ConnectionError(appveyor_request.text)
    else:
        anaconda_packages_request = anaconda_packages_request.json()
    files = []
    for anaconda_package_request in anaconda_packages_request:
        anaconda_url = "https://api.anaconda.org/packages/"
        anaconda_files_request = requests.get(anaconda_package_request['url'].replace('/packages/', '/package/') + '/files',
                                              headers=HEADERS)        
        if not anaconda_files_request.ok:
            raise ConnectionError(appveyor_request.text)
        else:
            anaconda_files_request = anaconda_files_request.json()
        for anaconda_file_request in anaconda_files_request:
            if anaconda_label in anaconda_file_request['labels']:
                filename = os.path.join(anaconda_label, anaconda_file_request['basename'].replace('/', os.sep))
                if not os.path.exists(filename) or force:
                    dirname = os.path.dirname(filename)
                    if not os.path.exists(dirname):
                        os.makedirs(dirname)
                    anaconda_url = "http:" + anaconda_file_request["download_url"]
                    anaconda_archive_request = requests.get(anaconda_url)
                    with open(filename, 'wb') as filehandler:
                        filehandler.write(anaconda_archive_request.content)

def upload(anaconda_owner=None, anaconda_label='main', force=True, register=True):
    anaconda_login, anaconda_password = retrieve()
    if anaconda_login and anaconda_password:
        if not anaconda_owner:
            anaconda_owner = repository["owner"]["login"]
    try:
        process = subprocess. Popen(["anaconda", "login", '--username', anaconda_login, '--password', anaconda_password], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        process.stdin.write("y".encode())
        process.communicate()
        process.stdin.close()
    except:
        raise
    anaconda_command = 'anaconda upload -u ' + anaconda_owner + ' -l ' + anaconda_label
    anaconda_command = anaconda_command.split(' ')
    for root, subdirs, files in os.walk(anaconda_label):
        anaconda_command.extend([os.path.join(root, file) for file in files if file.endswith('.tar.bz2')])
    if force:
        anaconda_command.append('-f')
    if register:
        anaconda_command.append('--register')
    subprocess.call(anaconda_command)

def clean(anaconda_owner=None, anaconda_label=None):
    anaconda_login, anaconda_password = retrieve()
    if anaconda_login and anaconda_password:
        if not anaconda_owner:
            anaconda_owner = repository["owner"]["login"]
    if anaconda_label is not None:
        try:
            process = subprocess.Popen(["anaconda", "login", '--username', anaconda_login, '--password', anaconda_password], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
            process.stdin.write("y".encode())
            process.communicate()
            process.stdin.close()
        except:
            raise
        anaconda_command = 'anaconda label --remove ' + anaconda_label + ' -o ' + anaconda_owner
        anaconda_command = anaconda_command.split(' ')
        subprocess.call(anaconda_command)
    anaconda_url = "https://api.anaconda.org/packages/" + anaconda_owner
    anaconda_packages_request = requests.get(anaconda_url,
                                             headers=HEADERS)
    if not anaconda_packages_request.ok:
        raise ConnectionError(appveyor_request.text)
    else:
        anaconda_packages_request = anaconda_packages_request.json()
    files = []
    for anaconda_package_request in anaconda_packages_request:
        anaconda_url = "https://api.anaconda.org/packages/"
        anaconda_files_request = requests.get(anaconda_package_request['url'].replace('/packages/', '/package/') + '/files',
                                              headers=HEADERS)        
        if not anaconda_files_request.ok:
            raise ConnectionError(appveyor_request.text)
        else:
            anaconda_files_request = anaconda_files_request.json()
        for anaconda_file_request in anaconda_files_request:
            if not anaconda_file_request['labels']:
                anaconda_delete_command = 'anaconda remove ' + anaconda_file_request["full_name"]
                anaconda_delete_command = anaconda_delete_command.split(' ')
                process = subprocess.Popen(anaconda_delete_command, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
                process.stdin.write("y".encode())
                process.communicate()
                process.stdin.close()