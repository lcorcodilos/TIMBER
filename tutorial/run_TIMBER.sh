#!/bin/bash
echo "Run script starting"
ls
source /cvmfs/cms.cern.ch/cmsset_default.sh
xrdcp root://cmseos.fnal.gov//store/user/cmsdas/2021/long_exercises/BstarTW/CMSDAS2021env.tgz ./
export SCRAM_ARCH=slc7_amd64_gcc820
tar -xzvf CMSDAS2021env.tgz
rm CMSDAS2021env.tgz
rm *.root

mkdir tardir; cp tarball.tgz tardir/; cd tardir/
tar -xzf tarball.tgz; rm tarball.tgz
cp -r * ../CMSSW_11_0_1/src/BstarToTW_CMSDAS2021/; cd ../CMSSW_11_0_1/src/
eval `scramv1 runtime -sh`
rm -rf timber-env
python -m virtualenv timber-env
source timber-env/bin/activate
cd TIMBER
source setup.sh
cd ../

echo python bs_select.py $*
python bs_select.py $*

xrdcp -f Presel_*.root root://cmseos.fnal.gov//store/user/cmantill/bstar_select_tau21_18/
