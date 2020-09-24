if grep -q '${TIMBERPATH}' <<< '${PATH}'
then
  echo 'TIMBER already on PATH'
else
  export PATH=${PATH}:$TIMBERPATH/Framework:$TIMBERPATH/data
  echo 'TIMBER added to PATH'
fi