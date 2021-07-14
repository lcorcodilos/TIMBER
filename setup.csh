#!/usr/bin/env tcsh
if ("$VIRTUAL_ENV" == "") then
  echo "ERROR: Create and activate a virtual environment and try again"
  return
endif

if (`command -v dot` == "") then
  echo "dot (graphviz) could not be found. Please install it first... (on Ubuntu 'sudo apt-get install graphviz libgraphviz-dev')"
  return
endif

python setup.py develop
set activate_path=$VIRTUAL_ENV/bin/activate.csh
setenv TIMBERPATH "$PWD/"

if (`grep -q $TIMBERPATH $activate_path` != "") then
  echo "TIMBER path already in activate"
else 
  printf "\n\n" > activate_ext.csh.cpy
  echo "setenv TIMBERPATH ${TIMBERPATH}" >> activate_ext.csh.cpy
  cat activate_ext.csh >> activate_ext.csh.cpy
  tcsh activate_ext.csh.cpy
  cat activate_ext.csh.cpy >> $activate_path
  rm activate_ext.csh.cpy
endif

if ! (-d "bin/libarchive") then
  git clone https://github.com/libarchive/libarchive.git
  cd libarchive
  cmake . -DCMAKE_INSTALL_PREFIX=../bin/libarchive
  make
  make install
  cd ..
  rm -rf libarchive
endif

if !(-d "bin/libtimber") then
  make
endif
