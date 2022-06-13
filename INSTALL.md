#TIMBER installation instructions

```
cmsrel CMSSW_12_3_0
cd CMSSW_12_3_0
cmsenv
cd ..
python3 -m virtualenv timber-env
source timber-env/bin/activate
git clone --branch Zbb_branch git@github.com:mroguljic/TIMBER.git
```
```
cd TIMBER/
mkdir bin
cd bin
git clone git@github.com:fmtlib/fmt.git
cd ../..
```
#Path may change depending on scram arch (the boost version as well!) so this needs to be modified by hand
```
cat <<EOT >> timber-env/bin/activate

export BOOSTPATH=/cvmfs/cms.cern.ch/slc7_amd64_gcc10/external/boost/1.75.0/lib
if grep -q '\${BOOSTPATH}' <<< '\${LD_LIBRARY_PATH}'
then
  echo 'BOOSTPATH already on LD_LIBRARY_PATH'
else
  export LD_LIBRARY_PATH=\${LD_LIBRARY_PATH}:\${BOOSTPATH}
  echo 'BOOSTPATH added to PATH'
fi
EOT

cd ..
source setup.sh
```

