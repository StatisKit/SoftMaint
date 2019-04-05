import requests
import json
import validators
import git
import os
import webbrowser

from requests.exceptions import ConnectionError
from requests.auth import HTTPBasicAuth

from . import config
from . import credential
from .__version__ import __version__

HEADERS = {'user-agent': 'GitHubDevOpsClient/' + __version__,
           'accept':'application/vnd.github.v3+json',
           'host':'https://api.github.com',
           'content-type': 'application/json'}

LICENSES = ['mit',
            'lgpl-3.0',
            'mpl2.0',
            'agpl-3.0',
            'unlicense',
            'apache-2.0',
            'gpl-3.0']

GITHUB_AUTH = None

def retrieve(login=None, password=None):
    if login is None:
        login = os.environ.get('GITHUB_LOGIN', None)
    if password is None:
        password = os.environ.get('GITHUB_PASSWORD', None)
    login, password = credential.retrieve('github.com',
                                          login=login,
                                          password=password)
    credential.__CACHE__['github.com'] = dict(login = login,
                                              password = password,
                                              account = None)
    return login, password

def authenticate(login=None, password=None):
    global GITHUB_AUTH
    login, password = retrieve(login=login, password=password)
    if not login or not password:
        raise ConnectionError("GitHub credential must be provided")
    GITHUB_AUTH = HTTPBasicAuth(login, password)

def _fetch(repository):
    if not validators.url(repository):
        repository = git.Repo(repository)
        return _fetch(repository.remote().url)
    else:
        github_url = repository.replace("http:", "https:").replace(".git", "").replace("/github.com/", "/api.github.com/repos/")
        github_request = requests.get(github_url,
                                      auth=GITHUB_AUTH)
        if not github_request.ok:
            raise ConnectionError(github_request.text)
        else:
            github_request = github_request.json()
        return github_request

def fetch(repository):
    authenticate()
    return _fetch(repository)

def rate_limit():
    authenticate()
    github_url = "https://api.github.com/rate_limit"
    github_request = requests.get(github_url,
                                  auth=GITHUB_AUTH)
    if not github_request.ok:
        raise ConnectionError(github_request.text)
    else:
        print(github_request.text)

def init(name, description="",
               homepage="",
               private=False,
               has_issues=True,
               has_projects=True,
               has_wiki=False,
               license=None,
               owner=None):
    authenticate()
    if not owner:
        github_url = "https://api.github.com/user/repos"
    else:
        github_url = "https://api.github.com/orgs/" + owner + "/repos"
    github_data = dict(name = name,
                       description = description,
                       homepage = homepage,
                       private = private,
                       has_issues = has_issues,
                       has_projects = has_projects,
                       has_wiki = has_wiki,
                       license_template = license)
    github_request = requests.post(github_url,
                                   auth=GITHUB_AUTH,
                                   data=json.dumps(github_data))
    if not github_request.ok:
        raise ConnectionError(github_request.text)
    else:
        github_request = github_request.json()
    return _fetch(github_request['html_url'])

def fork(owner, name):
    authenticate()
    github_url = "https://api.github.com/repos/" + owner + "/" + name + "/forks"
    github_request = requests.post(github_url,
                                   auth=GITHUB_AUTH)
    if not github_request.ok:
        raise ConnectionError(github_request.text)
    else:
        github_request = github_request.json()
    return _fetch(github_request['html_url'])

def clone(name, to_path=None, owner=None, recursive=True):
    login, password = retrieve()
    authenticate(login=login, password=password)
    if not owner:
        github_url = "https://github.com/" + login + "/" + name
    else:
        github_url = "https://github.com/" + owner + "/" + name
    if to_path is None:
        to_path = name
    local = git.Repo.clone_from(github_url, to_path)
    origin = _fetch(github_url)
    if "parent" in origin:
        local.create_remote("upstream", origin["parent"]["html_url"])
    return local

def deinit(name, owner=None):
    login, password = retrieve()
    authenticate(login=login, password=password)
    if not owner:
        github_url = "https://api.github.com/repos/" + login + "/" + name
    else:
        github_url = "https://api.github.com/repos/" + owner + "/" + name
    github_request = requests.delete(github_url,
                                   auth=GITHUB_AUTH)
    if not github_request.ok:
        raise ConnectionError(github_request.text)

def issues(repository=None, browser=False, assigned=False):
    if repository:
        repository = git.Repo(repository)
    login, password = retrieve()
    if browser:
        try:
            github_url = repository.remote('upstream').url
        except:
            github_url = repository.remote().url
        github_url += "/issues"
        if assigned:
            github_url += "/assigned/" + login
        webbrowser.open(github_url)
    else:
        authenticate(login=login, password=password)
        if repository:
            github_url = repository.remote().url
            upstream = _fetch(github_url)
            if "parent" in upstream:
                upstream = upstream["parent"]
            github_url = upstream["issues_url"].replace('{/number}', '')
            github_request = requests.get(github_url,
                                          auth=GITHUB_AUTH)
            if not github_request.ok:
                raise ConnectionError(github_request.text)
            else:
                github_request = github_request.json()
            length = 0
            for issue in github_request:
                if not assigned or any(assignee["login"] == login for assignee in issue["assignees"]):
                    length = max(len(str(issue["number"])), length)
            for issue in github_request:
                if not assigned or any(assignee["login"] == login for assignee in issue["assignees"]):
                    print("#" + str(issue["number"]).zfill(length) + ": " + issue["title"])
        else:
            github_url = 'https://api.github.com/user/issues'
            github_request = requests.get(github_url,
                                          auth=GITHUB_AUTH)
            if not github_request.ok:
                raise ConnectionError(github_request.text)
            else:
                github_request = github_request.json()
            length = 0
            for issue in github_request:
                if issue['state'] == "ppen":
                    
                    
                    issue['url']
                    title = "[" + issue['repository_url'].replace("https://api.github.com/repos/", "").replace("/", "::") + "#" + str(issue["number"]) + "] " + issue['title']
                    body = issue['body']
                length = max(len(str(issue["number"])), length)
            for issue in github_request:
                if not assigned or any(assignee["login"] == login for assignee in issue["assignees"]):
                    print("#" + str(issue["number"]).zfill(length) + ": " + issue["title"])

def _issue(repository, number):
    github_url = repository.remote().url
    upstream = _fetch(github_url)
    if "parent" in upstream:
        upstream = upstream["parent"]
    github_url = upstream["issues_url"].replace('{/number}', '/' + number)
    github_request = requests.get(github_url,
                                  auth=GITHUB_AUTH)
    if not github_request.ok:
        raise ConnectionError(github_request.text)
    else:
        github_request = github_request.json()
    return github_request

def issue(repository, number, browser=False):
    repository = git.Repo(repository)
    if number is None:
        branchname = repository.active_branch.name
        for branchtype in ["hotfix", "feature"]:
            if branchname.startswith(branchtype):
                number = int(branch.replace(branchtype + "_", ""))
                break
        if number is None:
            raise ValueError("cannot guess the issue number for an active branch named '" + branchname + "'")
    login, password = retrieve()
    number = str(number)
    if browser:
        try:
            github_url = repository.remote('upstream').url
        except:
            github_url = repository.remote().url
        github_url += "/issues/" + number
        webbrowser.open(github_url)
    else:
        authenticate(login=login, password=password)
        github_request = _issue(repository, number)
        print(github_request["title"] + " #" + number + "\n\n" + github_request["body"])

def _branch_from_issue(repository, number, prefix, default_remote, remote=None, label=None):
    repository = git.Repo(repository)
    login, password = retrieve()
    authenticate(login=login, password=password)
    number = str(number)
    try:
        issue = _issue(repository, number)
        try:
            repository.git.checkout('HEAD', b=prefix + '_' + str(number))
            _remote = None
            for branch in repository.git.branch('-r').splitlines():
                __remote = branch.split('/')[0]
                if branch == prefix + '_' + str(number):
                    _remote = __remote
                    break
            if _remote is not None and remote is not None and not remote == _remote:
                raise ValueError('A remote branch with the same name but a different remote already exists')
            elif remote is None:
                if _remote is None:
                    remote = default_remote
                else:
                    remote = _remote
            repository.git.push("--set-upstream", repository.remote(remote).url.replace('github.com', login + ":" + password + "@github.com"), prefix + "_" + str(number))
            for key in issue.keys():
                if key == "url":
                    github_url = issue.pop("url")
                elif not key in ["title", "body", "state", "milestone", "labels", "assignees"]:
                    issue.pop(key) 
            issue["state"] = "open"
            issue["assignees"] = [assignee["login"] for assignee in issue["assignees"]]
            if not login in issue["assignees"]:
                issue["assignees"].append(login)
            if label and not label in issue["labels"]:
                issue["labels"].append(label) 
            github_request = requests.patch(github_url,
                                            data=json.dumps(issue),
                                            auth=GITHUB_AUTH)
            if not github_request.ok:
                raise ConnectionError(github_request.text)
        except Exception as e:
            repository.git.checkout(prefix + "_" + str(number))
        config.load()
        config.__CACHE__["active_branch"] = prefix + "_" + str(number)
        config.register()
    except Exception as e:
        raise Exception("Issue #" + str(number) + " not found")

def hotfix(repository, number, remote=None):
    _branch_from_issue(repository, number, prefix="hotfix", default_remote="upstream", remote=remote, label="bug")

def feature(repository, number, remote=None):
    _branch_from_issue(repository, number, prefix="feature", default_remote="origin", remote=remote, label="enhancement")

def start(repository, branch=None):
    repository = git.Repo(repository)
    if branch is None:
        config.load()
        branch = config.__CACHE__.get('active_branch', None)
    if branch is None:
        raise ValueError("no active branch has been found")
    repository.git.checkout(branch)

def end(repository, suggest=False):
    if suggest:
        login, password = retrieve()
        authenticate(login=login, password=password)
        upstream = _fetch(repository)
        if "parent" in upstream:
            upstream = upstream["parent"]
        repository = git.Repo(repository)
        number = int(repository.active_branch.name.replace("hotfix_", "").replace("feature_", ""))
        if not login in repository.active_branch.tracking_branch().name.replace(login + ':' + password + '@', ''):
            head = repository.active_branch.name
        else:
            head = login + ":" + repository.active_branch.name
        github_url = upstream["url"] + "/pulls"
        github_data = dict(issue = number,
                           head = head,
                           base = 'master')
        github_request = requests.post(github_url,
                                       auth=GITHUB_AUTH,
                                       data=json.dumps(github_data))
        if not github_request.ok:
            raise ConnectionError(github_request.text)
        else:
            github_request = github_request.json()
    else:
        repository = git.Repo(repository)
    config.load()
    config.__CACHE__["active_branch"] = repository.active_branch.name
    config.register()
    repository.git.checkout("master")