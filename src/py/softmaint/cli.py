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
## file except in compliance with the License.You should have received a ##
## copy of the Apache License, Version 2.0 along with this file; see the ##
## file LICENSE. If not, you may obtain a copy of the License at         ##
##                                                                       ##
##     http://www.apache.org/licenses/LICENSE-2.0                        ##
##                                                                       ##
## Unless required by applicable law or agreed to in writing, software   ##
## distributed under the License is distributed on an "AS IS" BASIS,     ##
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or       ##
## mplied. See the License for the specific language governing           ##
## permissions and limitations under the License.                        ##

from path import Path
import argparse

from .walkfiles import main as walkfiles
from .notice import insert_notice

def main_notice():

    parser = argparse.ArgumentParser()
    parser.add_argument('directory',
                        help  = 'The directory in which files need to include NOTICE as a license header',
                        nargs ='?',
                        default = '.')
    parser.add_argument('notice',
                        help  = 'The file containing the content of include as files\' license header',
                        nargs ='?',
                        default = 'NOTICE')
    parser.add_argument('--back-up',
                        dest='back_up',
                        action='store_true',
                        help="")
    parser.add_argument('--no-back-up',
                        dest='back_up',
                        action='store_false')
    parser.set_defaults(back_up=False)
    parser.add_argument('--do',
                        dest='do',
                        action='store_true',
                        help="")
    parser.add_argument('--undo',
                        dest='do',
                        action='store_false',
                        help="")
    parser.set_defaults(do=True)
    args = parser.parse_args()

    notice = Path(args.directory)/args.notice
    if not notice.exists():
        raise ValueError("'notice' argument is invalid")
    with open(notice, 'r') as filehandler:
        notice = filehandler.read()

    for filepath in walkfiles(args.directory):
        if args.do:
            insert_notice(filepath, notice, args.back_up)
        elif (filepath + ".back").exists():
            with open(filepath + ".back", "r") as filehandler:
                content = filehandler.read()
            with open(filepath, "w") as filehandler:
                filehandler.write(content)