import sys
import unittest
import six
import shutil

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
 
    def test_00(self, owner=None):
        """Test `github init` and `github deinit` commands without owner"""
        sys.argv = ['github',
                    'init',
                    self.name,
                    '--description=' + self.description,
                    '--homepage=' + self.homepage,
                    '--license=' + self.license]
        if owner is not None:
            sys.argv += ['--owner=' + owner]
        cli.main_github()
        sys.argv = ['github',
                    'deinit',
                    self.name]
        if owner is not None:
            sys.argv += ['--owner=' + owner]
        cli.main_github()

    def test_01(self):
        """Test `github init` and `github deinit` commands with owner"""
        self.test_00(owner=self.owner)

    # def test_02(self):
    #     """Test `github fork`, `github issues` and `github issue` commands"""
    #     sys.argv = ['github',
    #                 'fork',
    #                 'devops-tools',
    #                 '--owner=' + self.owner]
    #     cli.main_github()
    #     sys.argv = ['github',
    #                 'clone',
    #                 'devops-tools']
    #     cli.main_github()
    #     old_stdout = sys.stdout
    #     new_stdout = StringIO()
    #     sys.stdout = new_stdout
    #     sys.argv = ['github',
    #                 'issues',
    #                 'devops-tools']
    #     cli.main_github()
    #     sys.stdout = old_stdout
    #     self.assertIn("#2: Test commands", new_stdout.getvalue())
    #     old_stdout = sys.stdout
    #     new_stdout = StringIO()
    #     sys.stdout = new_stdout
    #     sys.argv = ['github',
    #                 'issues',
    #                 'devops-tools',
    #                 '--assigned']
    #     cli.main_github()
    #     sys.stdout = old_stdout
    #     self.assertIn("#2: Test commands", new_stdout.getvalue())
    #     old_stdout = sys.stdout
    #     new_stdout = StringIO()
    #     sys.stdout = new_stdout
    #     sys.argv = ['github',
    #                 'issue',
    #                 'devops-tools',
    #                 '2']
    #     cli.main_github()
    #     sys.stdout = old_stdout
    #     self.assertEqual("Test commands #2\n\nThis is a fake issue that is used to test commands related to issues.\r\nIt must contains at least 2 lines.\n", new_stdout.getvalue())
    #     sys.argv = ['github',
    #                 'deinit',
    #                 'devops-tools']
    #     cli.main_github()
    #     shutil.rmtree('devops-tools')

    def test_03(self):
        """Test `github fork` and `github feature` commands"""
        sys.argv = ['github',
                    'fork',
                    'devops-tools',
                    '--owner=' + self.owner]
        cli.main_github()
        sys.argv = ['github',
                    'clone',
                    'devops-tools']
        cli.main_github()
        sys.argv = ['github',
                    'feature',
                    'devops-tools',
                    '--issue=2']
        cli.main_github()
        # sys.argv = ['github',
        #             'deinit',
        #             'devops-tools']
        # cli.main_github()
        shutil.rmtree('devops-tools')