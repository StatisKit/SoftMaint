import sys
import unittest
import six
import shutil
import os
import subprocess

if six.PY2:
    from StringIO import StringIO
else:
    from io import StringIO

from devops_tools import cli, github

from nose.plugins.attrib import attr
@attr(linux=True, 
      osx=True,
      win=True,
      level=1)
class TestGitHub(unittest.TestCase):

    name = "devops-test"
    description = "Repository created for devops-tools tests"
    homepage = "http://statiskit.rtfd.io"
    license = "apache-2.0"
    owner = "StatisKit"
 
    def _init(self, owner):
        sys.argv = ['github',
                    'init',
                    self.name,
                    '--description=' + self.description,
                    '--homepage=' + self.homepage,
                    '--license=' + self.license]
        if owner is not None:
            sys.argv += ['--owner=' + owner]
        cli.main_github()

    def _deinit(self, owner):
        sys.argv = ['github',
                    'deinit',
                    self.name]
        if owner is not None:
            sys.argv += ['--owner=' + owner]
        cli.main_github()
        if os.path.exists(self.name):
            shutil.rmtree(self.name)

    def _fork(self):
        sys.argv = ['github',
                    'fork',
                    self.name,
                    '--owner=' + self.owner]
        cli.main_github()

    def _clone(self):
        sys.argv = ['github',
            'clone',
            self.name]
        cli.main_github()

    def _issue(self):
        github.authenticate()
        repository = git.Repo(self.name)
        github_url = repository.remote().url
        upstream = _fetch(github_url)
        if "parent" in upstream:
            upstream = upstream["parent"]
        github_url = upstream["issues_url"].replace('{/number}', '/' + number)
        github_data = dict(title="Test commands",
                           body="This is a fake issue that is used to test commands related to issues.\r\nIt must contains at least 2 lines.")
        github_request = requests.post(github_url,
                                      auth=GITHUB_AUTH)
        if not github_request.ok:
            raise ConnectionError(github_request.text)

    def test_00(self, owner=None):
        """Test `github init` and `github deinit` commands without owner"""
        self._init(owner=owner)
        self._deinit(owner=owner)

    def test_01(self):
        """Test `github init` and `github deinit` commands with owner"""
        self.test_00(owner=self.owner)

    def test_02(self):
        """Test `github fork`, `github issues` and `github issue` commands"""
        self._init(owner=self.owner)
        self._fork()
        self._clone()
        self._issue()

        old_stdout = sys.stdout
        new_stdout = StringIO()
        sys.stdout = new_stdout
        sys.argv = ['github',
                    'issues',
                    self.name]
        cli.main_github()
        sys.stdout = old_stdout
        self.assertIn("#1: Test commands", new_stdout.getvalue())
        old_stdout = sys.stdout
        new_stdout = StringIO()
        sys.stdout = new_stdout
        sys.argv = ['github',
                    'issues',
                    self.name,
                    '--assigned']
        cli.main_github()
        sys.stdout = old_stdout
        self.assertIn("#1: Test commands", new_stdout.getvalue())
        old_stdout = sys.stdout
        new_stdout = StringIO()
        sys.stdout = new_stdout
        sys.argv = ['github',
                    'issue',
                    self.name,
                    '1']
        cli.main_github()
        sys.stdout = old_stdout
        self.assertEqual("Test commands #1\n\nThis is a fake issue that is used to test commands related to issues.\r\nIt must contains at least 2 lines.\n", new_stdout.getvalue())

        # self._deinit()
        # self._deinit(owner=owner)

    # def test_03(self, branch="feature"):
    #     """Test `github fork`, `github feature`, `github start` and `github end` commands"""
    #     sys.argv = ['github',
    #                 'fork',
    #                 'devops-tools',
    #                 '--owner=' + self.owner]
    #     cli.main_github()
    #     sys.argv = ['github',
    #                 'clone',
    #                 'devops-tools']
    #     cli.main_github()
    #     sys.argv = ['github',
    #                 branch,
    #                 'devops-tools',
    #                 '--issue=2']
    #     cli.main_github()
    #     sys.argv = ['github',
    #                 'end',
    #                 'devops-tools']
    #     cli.main_github()
    #     sys.argv = ['github',
    #                 'start',
    #                 'devops-tools']
    #     cli.main_github()
    #     subprocess.call(['git', '-C', 'devops-tools', 'commit', '--allow-empty', '-m"An empty commit for testing pull requests"'])
    #     subprocess.call(['git', '-C', 'devops-tools', 'push'])
    #     sys.argv = ['github',
    #                 'end',
    #                 'devops-tools',
    #                 '--suggest']
    #     cli.main_github()
    #     sys.argv = ['github',
    #                 'deinit',
    #                 'devops-tools']
    #     cli.main_github()
    #     shutil.rmtree('devops-tools')

    # def test_04(self):
    #     """Test `github fork`, `github hotfix`, `github start` and `github end` commands"""
    #     self.test_03(branch="hotfix")