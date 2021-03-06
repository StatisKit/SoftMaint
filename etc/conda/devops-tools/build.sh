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

set -ev

git config --system alias.co checkout
git config --system alias.br branch
git config --system alias.ci commit
git config --system alias.st status

if [[ "$PY3K" = 1 ]]; then
  2to3 -n -w $SRC_DIR/src/py/devops_tools
  # 2to3 -n -w $SRC_DIR/test
fi

$PYTHON setup.py install --prefix=$PREFIX

mkdir -p $PREFIX/etc/conda/activate.d
cp $RECIPE_DIR/activate.sh $PREFIX/etc/conda/activate.d/devops_tools_vars.sh

mkdir -p $PREFIX/etc/conda/deactivate.d
cp $RECIPE_DIR/deactivate.sh $PREFIX/etc/conda/deactivate.d/devops_tools_vars.sh


set +ev