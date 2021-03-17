# Goal: Equivalent result as example 2 but structured with VarGroups and CutGroups. 
# Cover some of the common mistakes via NOTES.
# Prerequisite: Requires having a valid proxy for xrootd

from TIMBER.Analyzer import *
from TIMBER.Tools.Common import *
import ROOT,sys

sys.path.append('../../')

# Enable using 4 threads
ROOT.ROOT.EnableImplicitMT(4)

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
myCuts.Add('njet','nFatJet>1') # NOTE: need to ensure two fat jets exist or next line will seg fault
myCuts.Add('pt_cut','FatJet_pt[0] > 400 && FatJet_pt[1] > 400')
myCuts.Add('eta_cut','FatJet_eta[0] < 2.4 && FatJet_eta[1] < 2.4')

###################
# Make a VarGroup #
###################
myVars = VarGroup('myVars')
myVars.Add('pt_sum','FatJet_pt[0] + FatJet_pt[1]')
myVars.Add('lead_vector','hardware::TLvector(FatJet_pt[0],FatJet_eta[0],FatJet_phi[0],FatJet_msoftdrop[0])')
myVars.Add('sublead_vector','hardware::TLvector(FatJet_pt[1],FatJet_eta[1],FatJet_phi[1],FatJet_msoftdrop[1])')
myVars.Add('invariantMass','hardware::InvariantMass({lead_vector,sublead_vector})') # Note that there are better ways to calculate this and this is an example

a.Apply([myCuts,myVars])

# Access the most recent node's data frame and make a histogram
myHist1 = a.GetActiveNode().DataFrame.Histo1D(('pt_sum','Sum of p_T of two leading jets',20,800,2000),'pt_sum')
myHist2 = a.GetActiveNode().DataFrame.Histo1D(('m_inv','Invariant mass of two leading jets',35,500,4000),'invariantMass')

# Also book a snapshot to save the FatJet_pt vectors and the pt_sum we've calculated in a TTree
out_vars = ['nFatJet','FatJet_pt','pt_sum','invariantMass'] # NOTE: need to save nFatJet so that ROOT knows how big the vectors in FatJet_pt are
a.GetActiveNode().Snapshot(out_vars,'ex3_out.root','mySnapshot',lazy=False,openOption='RECREATE') # RDataFrame loop executes here - everything else up to this point has been "lazy"

# Write out histograms after the snapshot (UPDATE not supported for snapshotting when multi-threading is enabled)
out = ROOT.TFile.Open('ex3_out.root','UPDATE')
myHist1.Write() 
myHist2.Write()
out.Close()
