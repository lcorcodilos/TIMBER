'''Plotting the Jet pT for jets that have a jet pT > 20 GeV and abs(jet eta) < 1.0.'''
import time
start = time.time()
#---------------------
from TIMBER.Analyzer import analyzer, HistGroup
a = analyzer('examples/GluGluToHToTauTau_full.root')
a.Define('JetSel_pt','Jet_pt[abs(Jet_eta) < 2.4]')
h = a.DataFrame.Histo1D('JetSel_pt')
h.Draw('hist e')
#---------------------
print ('%s secs'%(time.time() - start))