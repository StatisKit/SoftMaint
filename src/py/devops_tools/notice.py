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

import re
import warnings

from path import Path

SETTINGS = [dict(ext  = [".bat"],
                 left =  r':: '),
            dict(ext  = [".sh", ".py", ".yaml", ".yml"],
                 left =  '## '),
            dict(ext  = [".c", ".cc", ".cpp", ".c++", ".h"],
                 left = r'// '),
            dict(ext  = [".rst"],
                 left = r'.. ')]

for index, SETTING in enumerate(SETTINGS):
    if 'right' not in SETTING and 'left' in SETTING:
        SETTING['right'] = ''.join(reversed(SETTING['left']))
    elif 'left' not in SETTING and 'right' in SETTING:
        SETTING['left'] = ''.join(reversed(SETTING['right']))
    elif 'left' not in SETTING and 'right' not in SETTING:
        raise ValueError('invalid setting at position ' + str(index))

SETTINGS = {ext : SETTING for SETTING in SETTINGS for ext in SETTING['ext']}
SETTINGS['SConstruct'] = SETTINGS['.py']
SETTINGS['SConscript'] = SETTINGS['.py']

IGNORE = {".sublime-project",
          ".json"}

def setting(filepath):
    SETTING = SETTINGS.get(filepath.ext, SETTINGS.get(filepath.basename(), None))
    if SETTING is None:
        if filepath.ext not in IGNORE and filepath.basename() not in IGNORE:
            warnings.warn("No settings found for file '" + filepath + "'")
    return SETTING

def find(filepath):
    if not isinstance(filepath, Path):
        filepath = Path(filepath)
    if not(filepath.exists() or filepath.isfile()):
        raise ValueError("'filepath' parameter is not a valid path to a file")
    start = 0
    end = -1
    SETTING = setting(filepath)
    if SETTING is not None:
        with open(filepath, 'r') as filehandler:
            pattern = re.compile('^' + SETTING['left'] + '.*' + SETTING['right'] + '$')
            start = 0
            line = filehandler.readline()
            while line and not pattern.match(line):
                start += 1
                line = filehandler.readline()
            if not line:
                start = 0
            else:
                end = start
                line = filehandler.readline()
                while line and pattern.match(line):
                    end += 1
                    line = filehandler.readline()
    return start, end

def generate(filepath, notice):
    if not isinstance(filepath, Path):
        filepath = Path(filepath)
    if not(filepath.exists() or filepath.isfile()):
        raise ValueError("'filepath' parameter is not a valid path to a file")
    SETTING = setting(filepath)
    if SETTING is not None:
        lines = notice.splitlines()
        max_width = 0
        for index, line in enumerate(lines):
            line = line.rstrip()
            lines[index] = line
            max_width = max(max_width, len(line))
        return [SETTING["left"] + line + " " * (max_width - len(line)) + SETTING["right"] + "\n" for line in lines]

def replace(filepath, notice):
    if not isinstance(filepath, Path):
        filepath = Path(filepath)
    if not(filepath.exists() or filepath.isfile()):
        raise ValueError("'filepath' parameter is not a valid path to a file")
    SETTING = setting(filepath)
    if SETTING is not None:
        with open(filepath, "r") as filehandler:
            lines = list(filehandler.readlines())
        if len(lines) > 0:
            start, end = find(filepath)
            newlines = lines[:start]
            if start > 0 and lines[start - 1].strip():
                newlines += ["\n"]
            newlines += generate(filepath, notice)
            if end + 1 < len(lines):
                if lines[end + 1].strip():
                    newlines += ["\n"]
                newlines += lines[end + 1:]
        else:
            newlines = generate(filepath, notice)
    else:
        with open(filepath, "r") as filehandler:
            newlines = filehandler.readlines()
    return "".join(newlines)