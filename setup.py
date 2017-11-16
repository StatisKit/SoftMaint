import six
import os
from setuptools import setup, find_packages

packages = {"" : "src" + os.sep + "py"}
for package in find_packages("src" + os.sep + "py"):
    packages[package] = "src" + os.sep + "py"

with open('README.rst', 'r') as filehandler:
    long_description = filehandler.read()

setup(packages = packages.keys(),
      package_dir = {"" : "src" + os.sep + "py"},
      name = 'python-softmaint',
      version = '1.0.0',
      author = 'Pierre Fernique',
      author_email = 'pfernique@gmail.com',
      description = 'Tools to Ease Software Maintenance',
      long_description = '',
      license = 'Apache License 2.0',
      package_data = {package: [ "*.so", "*.dll"] for package in packages},
      entry_points = {
        'console_scripts': ['softmaint-license = softmaint.cli:license'],
        },
        zip_safe = True
    )
