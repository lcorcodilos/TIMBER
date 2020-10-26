'''Plotting the Jet pT (or any variable that is a per-event array).'''
import time
start = time.time()
#---------------------
from TIMBER.Analyzer import analyzer, HistGroup
a = analyzer('examples/GluGluToHToTauTau_full.root')
h = a.DataFrame.Histo1D('Jet_pt')
h.Draw('hist e')
#---------------------
print ('%s secs'%(time.time() - start))