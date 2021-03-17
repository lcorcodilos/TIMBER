# Goal: Building on example 3 with a correction added to generate
# shape templates. 
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

a.Apply([myCuts,myVars,topCuts])

# Add a correction
lead_sjbt_corr = Correction('lead_sjbtag_corr',
                       'TIMBER/Framework/src/SJBtag_SF.cc',
                       ['16','"DeepCSV"','"loose"'])
# Clone it and make the sublead version (cpObj to use same object instance of SJBtag_SF class)
sublead_sjbt_corr = lead_sjbt_corr.Clone('sublead_sjbtag_corr')
# Add both
a.AddCorrection(lead_sjbt_corr, evalArgs=['FatJet_pt[0]','FatJet_eta[0]'])
a.AddCorrection(sublead_sjbt_corr, evalArgs=['FatJet_pt[1]','FatJet_eta[1]'])

# Make weights based on the corrections
a.MakeWeightCols()

# Make HistGroup of uncertainty templates and draw them in pdf
templateGroup = a.MakeTemplateHistos(ROOT.TH1F('mtt','m_{tt}',30,500,3500), 'invariantMass')

a.DrawTemplates(templateGroup,'test_templates/')
a.PrintNodeTree('ex5_tree.png',verbose=True)
