#!/bin/bash
echo "Run script starting"
source /cvmfs/cms.cern.ch/cmsset_default.sh
export SCRAM_ARCH=slc7_amd64_gcc700
eval `scramv1 project CMSSW CMSSW_10_6_2`

mkdir tardir; cp tarball.tgz tardir/; cd tardir/
tar -xzf tarball.tgz; rm tarball.tgz
cp -r * ../CMSSW_10_6_2/src/; cd ../CMSSW_10_6_2/src/
cp JHUanalyzer/examples/tt16_preselection.py ./
eval `scramv1 runtime -sh`

echo python tt16_preselection.py $*
python tt16_preselection.py $*

cp tt16_presel_*.root ../../
