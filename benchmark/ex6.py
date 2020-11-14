'''Plot the Missing ET for events that have an opposite-sign muon
pair mass in the range 60-120 GeV (double loop over single collection, math)'''
import time
start = time.time()
#---------------------
from TIMBER.Analyzer import analyzer
from TIMBER.Tools.Common import CompileCpp
CompileCpp('benchmark/ex.cc')

a = analyzer('examples/GluGluToHToTauTau_full.root')
a.Cut('twoMuons','nMuon>1')
a.Define('invMassMuMu','InvMassOppMuMu(Muon_pt, Muon_eta, Muon_phi, Muon_mass, Muon_charge)')
a.Cut('invMassMuMu_cut','Any(invMassMuMu > 60 && invMassMuMu < 120)')
h = a.DataFrame.Histo1D('MET_pt')
h.Draw('hist e')
#---------------------
print ('%s secs'%(time.time() - start))