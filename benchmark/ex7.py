'''Plot the sum of the pT of jets with pT > 30 GeV that are not within 0.4 from any lepton with pt > 10 GeV (looping over two collections)'''
import time
start = time.time()
#---------------------
from TIMBER.Analyzer import analyzer
from TIMBER.Tools.Common import CompileCpp
CompileCpp('benchmark/ex.cc')

a = analyzer('examples/ttbar16_sample.root') # GluGlu sample is incomplete and missing electrons - this is a private stand in that must be replaced to work
a.MergeCollections("Lepton",["Electron","Muon"])
nearLep = 'CloseLepVeto (Lepton_pt, Lepton_eta, Lepton_phi, Jet_eta, Jet_phi)'
a.Define('goodJet_pt','Jet_pt[!(%s)]'%nearLep)
a.Define('goodJet_pt30','goodJet_pt[goodJet_pt > 30]')
a.Define('PtSum','Sum(goodJet_pt30)')
h = a.DataFrame.Histo1D('PtSum')
h.Draw('hist e')
#---------------------
print ('%s secs'%(time.time() - start))