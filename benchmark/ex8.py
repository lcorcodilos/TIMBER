'''Plot the transverse mass of the Missing ET and a lepton for events with at least
3 leptons and two of the leptons make up a Z (same flavor, opp sign, closest to invar
mass of 91.2 GeV), where the lepton being plotted is the third lepton.'''
# Lucas' Note: There could be four leptons in the event where two satisfy the Z condition
# and then either of the remaining two could be the one used in the transverse mass
# calculation. I do not consider that case (the first that comes up will be picked here).
import time
start = time.time()
#---------------------
from TIMBER.Analyzer import analyzer
from TIMBER.Tools.Common import CompileCpp
CompileCpp('benchmark/ex.cc')

a = analyzer('examples/ttbar16_sample.root') # GluGlu sample is incomplete and missing electrons - this is a private stand in that must be replaced to work
a.MergeCollections("Lepton",["Electron","Muon"])
a.Cut('nLepton2','nLepton>2')
a.Define('Lepton_vect','analyzer::TLvector(Lepton_pt, Lepton_eta, Lepton_phi, Lepton_mass)')
a.Define('NonZlep_idx','NonZlep(Lepton_vect,Lepton_pdgId,Lepton_charge)')
a.Define('MT','NonZlep_idx == -1 ? -1 : analyzer::transverseMass(MET_pt, Lepton_pt[NonZlep_idx], MET_phi, Lepton_phi[NonZlep_idx])')
a.Cut('MT_cut','MT>=0')
h = a.DataFrame.Histo1D('MT')
h.Draw('hist e')
#---------------------
print ('%s secs'%(time.time() - start))