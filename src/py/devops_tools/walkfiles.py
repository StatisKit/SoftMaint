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
import subprocess

def main(dirpath):
    if not isinstance(dirpath, Path):
        dirpath = Path(dirpath)
    if (dirpath/'.gitignore').exists():
        return git_walkfiles(dirpath)
    else:
        return fs_walkfiles(dirpath)

def fs_walkfiles(dirpath):
    if not isinstance(dirpath, Path):
        dirpath = Path(dirpath)
    filepaths = list(dirpath.walkfiles())
    return [filepath for filepath in filepaths if not filepath.basename() in ['NOTICE', 'LICENSE'] and not any(parent.startswith('.') for parent in filepath.relpath(dirpath).splitall()[1:])]

def git_walkfiles(dirpath, vcs=None):
    return [filepath for filepath in fs_walkfiles(dirpath) if git_ls(filepath)]

def git_ls(filepath):
    process = subprocess.Popen(['git', 'ls-files', filepath],
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    out, err = process.communicate()
    if out:
        return True
    else:
        return False