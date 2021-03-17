# Goal: Building on example 3 and assuming a boosted tt selection with more cuts and definitions,
# a forking of the selection, N-1 selections, and printing the workflow. 
# Prerequisite: Requires having a valid proxy for xrootd and graphviz installed for final line

from TIMBER.Analyzer import *
from TIMBER.Tools.Common import *
import ROOT,sys

sys.path.append('../../')

# Enable using 4 threads
ROOT.ROOT.EnableImplicitMT(1)

file_name = 'root://cms-xrd-global.cern.ch//store/mc/RunIISummer16NanoAODv6/TT_TuneCUETP8M2T4_13TeV-powheg-pythia8/NANOAODSIM/PUMoriond17_Nano25Oct2019_102X_mcRun2_asymptotic_v7-v2/20000/740B9BA3-8A64-B743-9439-2930CE247191.root'
# file_name = 'TIMBER/examples/ttbar16_sample.root'

# Import the C++
CompileCpp('TIMBER/Framework/include/common.h') # Compile (via gInterpreter) commonly used c++ code
CompileCpp('TIMBER/examples/example.cc') # Compile a full file 

# Create analyzer instance
a = analyzer(file_name)

###################
# Make a CutGroup #
###################
myCuts = CutGroup('myCuts')
myCuts.Add('njet',        'nFatJet>1') # NOTE: need to ensure two fat jets exist or next line will seg fault
myCuts.Add('pt_cut',      'FatJet_pt[0] > 400 && FatJet_pt[1] > 400')
myCuts.Add('eta_cut',     'FatJet_eta[0] < 2.4 && FatJet_eta[1] < 2.4')
myCuts.Add('tau2', 'FatJet_tau2[0] > 0 && FatJet_tau2[1] > 0')


###################
# Make a VarGroup #
###################
myVars = VarGroup('myVars')
myVars.Add('pt_sum',            'FatJet_pt[0] + FatJet_pt[1]')
myVars.Add('lead_vector',       'hardware::TLvector(FatJet_pt[0],FatJet_eta[0],FatJet_phi[0],FatJet_msoftdrop[0])')
myVars.Add('sublead_vector',    'hardware::TLvector(FatJet_pt[1],FatJet_eta[1],FatJet_phi[1],FatJet_msoftdrop[1])')
myVars.Add('invariantMass',     'hardware::InvariantMass({lead_vector,sublead_vector})') 
myVars.Add('tau32',        'tau32Maker(FatJet_tau3,FatJet_tau2)')
myVars.Add('subjet_btag',  'sjbtagMaker(FatJet_subJetIdx1,FatJet_subJetIdx2,SubJet_btagDeepB)')
myVars.Add('lead_mass', 'FatJet_msoftdrop[0]') # need to book these to plot mass
myVars.Add('sublead_mass', 'FatJet_msoftdrop[1]') # Cannot reference vector entry in Histo call
myVars.Add('lead_tau32','tau32[0]')
myVars.Add('sublead_tau32','tau32[1]')
myVars.Add('lead_sjbtag','subjet_btag[0]')
myVars.Add('sublead_sjbtag','subjet_btag[1]')

topCuts = CutGroup('topCuts')
topCuts.Add('lead_tau32_cut','lead_tau32 < 0.54')
topCuts.Add('sublead_tau32_cut','sublead_tau32 < 0.54')
topCuts.Add('lead_sjbtag_cut','lead_sjbtag > 0.15')
topCuts.Add('sublead_sjbtag_cut','sublead_sjbtag > 0.15')
topCuts.Add('lead_mass_cut','lead_mass > 105 && lead_mass < 220')
topCuts.Add('sublead_mass_cut','sublead_mass > 105 && sublead_mass < 220')

nodeToPlot = a.Apply([myCuts,myVars])

#########################################
# Do N-1 selections and draw histograms #
#########################################
# Organize N-1 of tagging variables when assuming top is always leading
nminus1Nodes = a.Nminus1(topCuts,nodeToPlot) # NOTE: Returns the nodes with N-1 selections
nminus1Hists = HistGroup('nminus1Hists') # NOTE: HistGroup used to batch operate on histograms

# Add hists to group and write out at the end
for nkey in nminus1Nodes.keys():
    if nkey == 'full': continue
    var = nkey.replace('_cut','').replace('minus_','')
    hist = nminus1Nodes[nkey].DataFrame.Histo1D(var)
    nminus1Hists.Add(var,hist)

#################################################
# Now apply the top cuts and return to workflow #
#################################################
# Access the most recent node's data frame and make a histogram
myHist2 = a.GetActiveNode().DataFrame.Histo1D(('m_inv','Invariant mass of two top jets',35,500,4000),'invariantMass')

# Also book a snapshot to save the FatJet_pt vectors and the pt_sum we've calculated in a TTree
out_vars = ['nFatJet','FatJet_pt','sublead_.*','lead_.*','invariantMass'] # NOTE: Can use regex to grab multiple columns at once
a.GetActiveNode().Snapshot(out_vars,'ex4_out.root','mySnapshot',lazy=False,openOption='RECREATE') # RDataFrame loop executes here - everything else up to this point has been 'lazy'

# Write out histograms after the snapshot (UPDATE not supported for snapshotting when multi-threading is enabled)
out = ROOT.TFile.Open('ex4_out.root','UPDATE')
nminus1Hists.Do('Write')
out.Close()

# NOTE: Can plot full node to tree to ensure selections were made accurately (requires graphviz python package and Graphviz installation)
a.PrintNodeTree('ex4_tree.png')