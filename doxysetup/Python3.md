# Getting a Python 3 compatible version of ROOT

For those unaware, ROOT must be built with a specific version of python. Most builds use Python 2.7 
for the sake of backwards compatibility with older python scripts. However, Python 2.7 reached 
end-of-life on January 1st, 2020 and is no longer supported. Given this and the fact that 
Python 3 has a lot of very nice features, everyone should start converting as soon as possible.

This is a guide to ensure your environment is ready for the switch.

**NOTE:** TIMBER is currently compatible with both Python 2.7 and Python 3 but support for Python 2.7
will soon be dropped. 

## Local/personal computer

ROOT version 6.22 has introduced support for being compatible with Python 2.7 and Python 3 simultaneously.
More information can be found [here](https://root.cern/install/build_from_source/#root-python-and-pyroot).
The simplest solution for your personal computer may be to just install v6.22 (either by building from
source or downloading the binary). General install instructions can be found [here](https://root.cern/install/).

If you'd like to use an older version of ROOT, you'll need to build from source with the cmake option
`-DPYTHON_EXECUTABLE=path/to/python` specified. Read [more](https://root.cern/install/build_from_source/#root-python-and-pyroot) for details.

## With CMSSW on LXPLUS or LPC

WARNING: THESE INSTRUCTIONS DO NOT WORK CONSISTENTLY ACROSS USE CASES.

There's no good resource that explains which CMSSW versions have which python and ROOT versions (if you know of one,
please send it to me and I'll add it here!). One can parse the information in `cvmfs` but these instructions are
so you can avoid that! CMSSW versions almost always come with some version of Python 2.7 and Python 3.x but 
current popular CMSSW versions have ROOT versions older than v6.22 and it is almost always compiled for Python 2.7 
for the sake of backwards compatibility with user scripts. 

This is incredibly unfortunate given that Python 3 has been available so long and that Python 2.7 is explicitly
not supported anymore. The best way to convince others that CMS as a collaboration needs to switch off of outdated
software is to convert yourself - even if you have to play tricks (like the following one) to get there.

The trick to get a Python 3 compatible version of ROOT is to just source the version of ROOT you want after your `cmsenv` by
sourcing another root version like `source /cvmfs/cms.cern.ch/slc7_amd64_gcc820/lcg/root/6.22.00/bin/thisroot.sh`.

This grabs the nice v6.22 so you can still use your Python 2.7 while you convert to Python 3. The problem is that this build of
v6.22 is for Python **3.8** compatibility which means one needs a CMSSW with Python 3.8. Feel free to test your favorite versions
of CMSSW but CMSSW_11_1_4 was the newest version of CMSSW (excluding `_pre` versions) that had Python 3.8 (at the time of writing). 

Here's the full setup.
```
cmsrel CMSSW_11_1_4 # has python 3.8 (root version we grab will be compiled for python3.8 but not python3.6)
cd CMSSW_11_1_4/src
cmsenv
source /cvmfs/cms.cern.ch/slc7_amd64_gcc820/lcg/root/6.22.00/bin/thisroot.sh # compiled for python2.7 and python3.8 (not for python3.6 which is why we need CMSSW_11_1_4)
python3 -c "import ROOT" # test python3 - should return nothing
python2.7 -c "import ROOT" # test python2.7 - should return nothing
```

Of course, this means that you need to source your root version manually after cmsenv. My recommendation around
this is to do one of two things:
1. Setup an alias in your `.bashrc` like `alias cmsenv_py3='cmsenv; source /cvmfs/cms.cern.ch/slc7_amd64_gcc820/lcg/root/6.22.00/bin/thisroot.sh'`.
Then use this alias instead of `cmsenv`.
2. Setup a python virtualenv and modify the activate script to run `source /cvmfs/cms.cern.ch/slc7_amd64_gcc820/lcg/root/6.22.00/bin/thisroot.sh`
at the end. 
```
cmsenv
python3 -m virtualenv pyroot3
echo -e "\nsource /cvmfs/cms.cern.ch/slc7_amd64_gcc820/lcg/root/6.22.00/bin/thisroot.sh" >> pyroot3/bin/activate
source pyroot3/bin/activate
```
With this option, you'll need to remember to activate the virtualenv every time after you cmsenv but in general,
virtualenvs are good to use so you can install other python packages via pip.

3. Combine (1) and (2) so that the alias also does the virtualenv activating.

(optional) If you want to be really cool, also modify the `deactivate` function in `pyroot3/bin/activate` so that it resets
the root version to the original for `CMSSW_11_1_4`. This is mainly for fun since you could perform the reset by calling `cmsenv`
as well.