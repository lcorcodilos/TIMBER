if grep -q '${new_path}' <<< '${PATH}'
then
  echo 'TIMBER already on PATH'
else
  export PATH=${PATH}:$new_path/Framework:$new_path/data
  echo 'TIMBER added to PATH'
fi