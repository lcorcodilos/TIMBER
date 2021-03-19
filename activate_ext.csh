if (`echo "$PATH" | grep "$TIMBERPATH"` == "") then
  setenv PATH ${PATH}:${TIMBERPATH}
  echo 'TIMBER added to PATH'
else
  echo 'TIMBER already on PATH'
endif
