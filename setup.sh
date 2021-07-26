#!/usr/bin/env bash
if [[ "$VIRTUAL_ENV" == "" ]]
then
  echo "ERROR: Create and activate a virtual environment and try again"
  return
fi

if ! command -v dot &> /dev/null
then
  echo "dot (graphviz) could not be found. Please install it first... (on Ubuntu 'sudo apt-get install graphviz libgraphviz-dev')"
  return
fi

python setup.py develop
activate_path=$VIRTUAL_ENV/bin/activate
export TIMBERPATH="$PWD/"

if grep -q $TIMBERPATH $activate_path
then
  echo "TIMBER path already in activate"
else 
  printf "\n\n" > activate_ext.sh.cpy
  echo "export TIMBERPATH=${TIMBERPATH}" >> activate_ext.sh.cpy
  cat activate_ext.sh >> activate_ext.sh.cpy
  source activate_ext.sh.cpy
  cat activate_ext.sh.cpy >> $activate_path
  rm activate_ext.sh.cpy
fi

if [ ! -d "bin/libarchive" ] 
then
  git clone https://github.com/libarchive/libarchive.git
  cd libarchive
  cmake . -DCMAKE_INSTALL_PREFIX=../bin/libarchive
  make
  make install
  cd ..
  rm -rf libarchive
fi

if [ ! -d "bin/libtimber" ]
then
  make
fi
