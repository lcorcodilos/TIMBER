'''Plotting the Missing ET (or any event level variable).'''
import time
start = time.time()
#---------------------
from TIMBER.Analyzer import analyzer
a = analyzer('examples/GluGluToHToTauTau_full.root')
h = a.DataFrame.Histo1D('MET_pt')
h.Draw('hist e')
#---------------------
print ('%s secs'%(time.time() - start))