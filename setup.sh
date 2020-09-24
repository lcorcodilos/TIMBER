#!/usr/bin/env bash
if [[ "$VIRTUAL_ENV" == "" ]]
then
  echo "ERROR: Create and activate a virtual environment and try again"
  return
fi

python setup.py install
activate_path=$VIRTUAL_ENV/bin/activate
new_path="$PWD/TIMBER/"

if grep -q $new_path $activate_path
then
  echo "TIMBER path already in activate"
else 
  printf "\n\n" > activate_ext.sh.cpy
  echo new_path=${PWD}/TIMBER/ >> activate_ext.sh.cpy
  cat activate_ext.sh >> activate_ext.sh.cpy
  source activate_ext.sh.cpy
  cat activate_ext.sh.cpy >> $activate_path
  rm activate_ext.sh.cpy
fi