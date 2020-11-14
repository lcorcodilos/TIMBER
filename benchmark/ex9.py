'''Create a group of plots (jet pT, eta, phi, N_jets). Now make
it for all events, for events with missing et > 20 GeV, and for
events with missing et > 20 GeV and 2 jets with 40 GeV and abs(eta)
< 1.0. Demonstrate making "groups" of plots, and a graphical cut flow'''
import time
start = time.time()
#---------------------
import ROOT
from TIMBER.Analyzer import analyzer

binning_tuples = {
    'Jet_pt': ('Jet_pt','Jet p_{T}',100,0,500),
    'Jet_eta': ('Jet_eta','Jet #eta',100,-5,5),
    'Jet_phi': ('Jet_phi','Jet #phi',100,-3.14,3.14),
    'nJet': ('nJet','Number of Jets',10,0,10)
}

a = analyzer('examples/GluGluToHToTauTau_full.root')
raw_hists = a.MakeHistsWithBinning(binning_tuples)
a.Cut('MET_cut','MET_pt>20')
METcut_hists = a.MakeHistsWithBinning(binning_tuples)
a.Cut('Jet_PtEta_cut','Sum(Jet_pt>40 && abs(Jet_eta)<1.0) > 1')
final_hists = a.MakeHistsWithBinning(binning_tuples)

all_hists = raw_hists+METcut_hists+final_hists

out_file = ROOT.TFile.Open('benchmark/ex9_hists.root','RECREATE')
all_hists.Do('Write')
out_file.Close()

a.PrintNodeTree('benchmark/ex9_tree.pdf')
#---------------------
print ('%s secs'%(time.time() - start))