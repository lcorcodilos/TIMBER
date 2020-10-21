'''Plot the sum of the pT of jets with pT > 30 GeV that are not within 0.4 from any lepton with pt > 10 GeV (looping over two collections)'''
import time
start = time.time()
#---------------------
from TIMBER.Analyzer import analyzer
from TIMBER.Tools.Common import CompileCpp
CompileCpp('TIMBER/Framework/include/common.h')

a = analyzer('examples/ttbar16_sample.root')
a.Define('Jet_pt30','Jet_pt[Jet_pt > 30]')
a.Define('Lepton_eta','Concatenate(Electron_eta,Muon_eta)')
a.Define('Lepton_phi','Concatenate(Electron_phi,Muon_phi)')
a.Define('Lepton_pt','Concatenate(Electron_pt,Muon_pt)')
nearLep = '(Lepton_pt > 10) && (analyzer::DeltaR(Lepton_eta, Jet_eta, Lepton_phi, Jet_phi) < 0.4)'
a.Define('goodJet_pt','Jet_pt30[!(%s)]'%nearLep)
a.Define('PtSum','Sum(goodJet_pt)')
print a.DataFrame.GetColumnType('PtSum')
h = a.DataFrame.Histo1D('PtSum')
h.Draw('hist e')
#---------------------
print ('%s secs'%(time.time() - start))