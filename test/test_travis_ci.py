from devops_tools import cli
from devops_tools import github
import time

import sys
import unittest
from nose.plugins.attrib import attr

@attr(linux=True, 
      osx=True,
      win=True,
      level=1)
class TestTravisCI(unittest.TestCase):

    name = "devops-test"
    description = "Repository created for devops-tools tests"
    homepage = "http://statiskit.rtfd.io"
    license = "apache-2.0"
    owner = "StatisKit"

    @classmethod
    def setUpClass(cls):
        cls.upstream = github.init(name=cls.name,
                                   description=cls.description,
                                   homepage=cls.homepage,
                                   license=cls.license,
                                   owner=cls.owner)
        cls.origin = github.fork(owner=cls.owner,
                                 name=cls.name)

    def test_00(self, remote="upstream"):
        """Test `travis_ci` command line"""
        sys.argv = ['travis_ci',
                    'init',
                    getattr(self, remote)["html_url"]]
        cli.main_travis_ci()
        time.sleep(5)
        sys.argv = ['travis_ci',
                    'deinit',
                    getattr(self, remote)["html_url"]]
        cli.main_travis_ci()

    def test_01(self):
        """Test `travis_ci` command line"""
        self.test_00(remote="origin")

    @classmethod
    def tearDownClass(cls):
        github.deinit(name=cls.name, owner=None)
        github.deinit(name=cls.name, owner=cls.owner)