import ROOT
from TIMBER.Analyzer import HistGroup, analyzer

a = analyzer('ZprimeToTT_M2000_W20_RunIIAutumn18NanoAODv7.root') # open file

trigDict = {
    "16": ['HLT_PFHT900','HLT_PFHT800','HLT_PFJet450'],
    "17": ['HLT_PFHT1050','HLT_PFJet500'],
    "18": ['HLT_PFHT1050','HLT_PFJet500']
}

a.Cut('trigger',a.GetTriggerString(trigDict['18']))
a.Cut('Flags',a.GetFlagString())
a.Cut('numberFatJets','nFatJet>1')
a.Cut('pt','FatJet_pt[0] > 400 && FatJet_pt[1] > 400') # will seg fault if nFatJet<=1 !!
a.Cut('eta','abs(FatJet_eta[0]) < 2.4 && abs(FatJet_eta[1]) < 2.4')
a.Cut('oppositeHemis','hardware::DeltaPhi(FatJet_phi[0], FatJet_phi[1]) > M_PI/2')
a.Cut('massLead','FatJet_msoftdrop[0] > 105 && FatJet_msoftdrop[0] < 210')
a.Cut('massSublead','FatJet_msoftdrop[1] > 105 && FatJet_msoftdrop[1] < 210')
a.Define('FatJet_vects','hardware::TLvector(FatJet_pt, FatJet_eta, FatJet_phi, FatJet_msoftdrop)')
a.Define('mtt','hardware::InvariantMass({FatJet_vects[0], FatJet_vects[1]})')

presel = a.Cut('DAK8_sublead','FatJet_deepTagMD_TvsQCD[1] > 0.9')
presel.Snapshot(['nFatJet','FatJet_.*'],'exercise3_tree.root','myFatJets',lazy=True)

hists = HistGroup('out')
# Signal region
SR_node = a.Cut('DAK8_lead','FatJet_deepTagMD_TvsQCD[0] > 0.9')
hists.Add(SR_node.DataFrame.Histo1D('mtt'))
# Go back
a.SetActiveNode(presel)
# Control region
CR_node = a.Cut('NotDAK8_lead','FatJet_deepTagMD_TvsQCD[0] < 0.9')
hists.Add(CR_node.DataFrame.Histo1D('mtt'))

out = ROOT.TFile.Open('exercise3.root','RECREATE')
out.cd()
hists.Do('Write')
out.Close()