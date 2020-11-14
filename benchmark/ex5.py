'''Plot the opposite-sign muon pair mass for all combinations of muons'''
import time
start = time.time()
#---------------------
from TIMBER.Analyzer import analyzer
from TIMBER.Tools.Common import CompileCpp
CompileCpp('benchmark/ex.cc')

a = analyzer('examples/GluGluToHToTauTau_full.root')
a.Cut('twoMuons','nMuon>1')
a.Define('invMassMuMu','InvMassOppMuMu(Muon_pt, Muon_eta, Muon_phi, Muon_mass, Muon_charge)')
h = a.DataFrame.Histo1D(('invMassMuMu','Invariant mass of opposite sign muon pairs',100,0,200),'invMassMuMu')
h.Draw('hist e')
#---------------------
print ('%s secs'%(time.time() - start))