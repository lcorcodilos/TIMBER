# Goal: Open a NanoAOD format file, apply a simple filter, calculate a new variable
# and plot a histogram of the new variable. Cover some of the common mistakes via NOTES
# Prerequisite: Requires having a valid proxy for xrootd

from TIMBER.Analyzer import *
import ROOT,sys

sys.path.append('../../')

# Enable using 4 threads
# ROOT.ROOT.EnableImplicitMT(4)

file_name = 'root://cms-xrd-global.cern.ch//store/mc/RunIISummer16NanoAODv6/TT_TuneCUETP8M2T4_13TeV-powheg-pythia8/NANOAODSIM/PUMoriond17_Nano25Oct2019_102X_mcRun2_asymptotic_v7-v2/20000/740B9BA3-8A64-B743-9439-2930CE247191.root'
# file_name = 'TIMBER/examples/ttbar16_sample.root'

# Create analyzer instance
a = analyzer(file_name)
# Since we're just testing, only run over first 100 events
# This is why we don't enable implicit multi-threading
a.Range(100)

# Apply a cut that the two leading fat jets have pt > 400
a.Cut('njet','nFatJet>1') # NOTE: need to ensure two fat jets exist or next line will seg fault
a.Cut('pt_cut','FatJet_pt[0] > 400 && FatJet_pt[1] > 400')
# Define the sum of the pt
a.Define('pt_sum','FatJet_pt[0] + FatJet_pt[1]')

# Access the most recent node's data frame and make a histogram
myHist = a.GetActiveNode().DataFrame.Histo1D(('pt_sum','Sum of p_T of two leading jets',20,800,2000),'pt_sum')

# Also book a snapshot to save the FatJet_pt vectors and the pt_sum we've calculated in a TTree
out_vars = ['nFatJet','FatJet_pt','pt_sum'] # NOTE: need to save nFatJet so that ROOT knows how big the vectors in FatJet_pt are
a.GetActiveNode().Snapshot(out_vars,'ex1_out.root','mySnapshot',lazy=False,openOption='RECREATE') # RDataFrame loop executes here - everything else up to this point has been "lazy"

# Write out histograms after the snapshot (UPDATE not supported for snapshotting when multi-threading is enabled)
out = ROOT.TFile.Open('ex1_out.root','UPDATE')
myHist.Write() 
out.Close()
