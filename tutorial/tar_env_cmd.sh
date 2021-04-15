cd $CMSSW_BASE/..
tar --exclude-caches-all --exclude-vcs --exclude-caches-all --exclude-vcs -cvzf TIMBER_tutorial.tgz CMSSW_11_1_4 --exclude=tmp --exclude=".scram" --exclude=".SCRAM"
cd $CMSSW_BASE/src