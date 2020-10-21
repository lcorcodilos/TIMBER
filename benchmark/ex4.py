'''Plotting the Missing ET for jets[sic?] with at least 2 jets with Jet pT > 40 and abs(jet Eta) < 1.0'''
import time
start = time.time()
#---------------------
from TIMBER.Analyzer import analyzer
a = analyzer('examples/GluGluToHToTauTau_full.root')
a.Cut('twoHighPtJets','Sum(Jet_pt > 40 && abs(Jet_eta) < 1.0) >= 2')
h = a.DataFrame.Histo1D('MET_pt')
h.Draw('hist e')
#---------------------
print ('%s secs'%(time.time() - start))