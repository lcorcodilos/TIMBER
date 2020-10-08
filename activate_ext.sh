if grep -q '${TIMBERPATH}' <<< '${PATH}'
then
  echo 'TIMBER already on PATH'
else
  export PATH=${PATH}:${TIMBERPATH}
  echo 'TIMBER added to PATH'
fi