# from devops_tools import (github,
#                           travis,
#                           appveyor)

# import unittest
# from nose.plugins.attrib import attr

# @attr(linux=True, 
#       osx=True,
#       win=True,
#       level=1)
# class TestGitHub(unittest.TestCase):

#     name = "devops-test"
#     description = "Repository created for devops-tools tests"
#     homepage = "http://statiskit.rtfd.io"
#     license="apache-2.0"
#     owner = "StatisKit"

#     @classmethod
#     def setUpClass(cls):
#         """Test repository initialization and forking with GitHub"""
#         try:
#             github.deinit(name=cls.name, owner=None)
#         except:
#             pass
#         try:
#             github.deinit(name=cls.name, owner=cls.owner)
#         except:
#             pass
#         cls.upstream = github.init(name=cls.name,
#                                    description=cls.description,
#                                    homepage=cls.homepage,
#                                    license=cls.license,
#                                    owner=cls.owner)
#         cls.origin = github.fork(owner=cls.owner,
#                                  name=cls.name)

#     def test_travis(self):
#         """Test Travis CI init/deinit with GitHub"""
#         travis.init(self.upstream)
#         travis.deinit(self.upstream)
#         travis.init(self.origin)
#         travis.deinit(self.origin)

#     def test_appveyor(self):
#         """Test AppVeyor CI init/deinit with GitHub"""
#         appveyor.init(self.upstream)
#         appveyor.deinit(self.upstream)
#         appveyor.init(self.origin)
#         appveyor.deinit(self.origin)

#     @classmethod
#     def tearDownClass(cls):
#         """Test repository deinit with GitHub"""
#         github.deinit(name=cls.name, owner=None)
#         github.deinit(name=cls.name, owner=cls.owner)