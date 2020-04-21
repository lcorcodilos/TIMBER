import ROOT
ROOT.ROOT.EnableImplicitMT(4)

import time, os
from optparse import OptionParser

from JHUanalyzer.Analyzer.analyzer import analyzer,openJSON
from JHUanalyzer.Analyzer.Cscripts import CommonCscripts, CustomCscripts
commonc = CommonCscripts()
customc = CustomCscripts()

parser = OptionParser()

parser.add_option('-i', '--input', metavar='F', type='string', action='store',
                default   =   '',
                dest      =   'input',
                help      =   'A root file or text file with multiple root file locations to analyze')
parser.add_option('-o', '--output', metavar='FILE', type='string', action='store',
                default   =   'output.root',
                dest      =   'output',
                help      =   'Output file name.')
parser.add_option('-c', '--config', metavar='FILE', type='string', action='store',
                default   =   'config.json',
                dest      =   'config',
                help      =   'Configuration file in json format that is interpreted as a python dictionary')


(options, args) = parser.parse_args()

start_time = time.time()

a = analyzer(options.input)
if '_loc.txt' in options.input: setname = options.input.split('/')[-1].split('_loc.txt')[0]
else: setname = ''

if os.path.exists(options.config):
    print('JSON config imported')
    c = openJSON(options.config)
    if setname != '' and not a.isData: 
        xsec = c['XSECS'][setname]
        lumi = c['lumi']
    else: 
        xsec = 1.
        lumi = 1.


a.SetCFunc("deltaPhi",commonc.deltaPhi)
a.SetCFunc("TLvector",commonc.vector)
a.SetCFunc("invariantMass",commonc.invariantMass)
customc.Import("subjet_btag","JHUanalyzer/examples/c_scripts/subjet_btag.cpp")
a.SetCFunc("subjet_btag",customc.subjet_btag)
# a.SetCFunc("HT",commonc.HT)

a.SetTriggers(["HLT_AK8PFJet450","HLT_AK8PFJet360_TrimMass30","HLT_AK8PFHT750_TrimMass50","HLT_PFHT800","HLT_PFHT900"])
a.SetCut("nFatJets","nFatJet > 1")
a.SetCut("pt0","FatJet_pt[0] > 400")
a.SetCut("pt1","FatJet_pt[1] > 400")
a.SetCut("eta0","abs(FatJet_eta[0]) < 2.4")
a.SetCut("eta1","abs(FatJet_eta[1]) < 2.4")
a.SetCut("HT","(FatJet_pt[0]+FatJet_pt[1]) > 950")
a.SetCut("deltaPhi","abs(analyzer::deltaPhi(FatJet_phi[0],FatJet_phi[1])) > 2.1")
a.SetCut("jetID","((FatJet_jetId[0] & 2) == 2) && ((FatJet_jetId[1] & 2) == 2)")

# Top Tagging
a.SetCut("tau32","(FatJet_tau3[0]/FatJet_tau2[0] < 0.65) && (FatJet_tau3[1]/FatJet_tau2[1] < 0.65)")
a.SetCut("msoftdrop_0","105 < FatJet_msoftdrop[0] && FatJet_msoftdrop[0] < 210")
a.SetCut("msoftdrop_1","105 < FatJet_msoftdrop[1] && FatJet_msoftdrop[1] < 210")

a.SetVar("lead_vect","analyzer::TLvector(FatJet_pt[0],FatJet_eta[0],FatJet_phi[0],FatJet_msoftdrop[0])")
a.SetVar("sublead_vect","analyzer::TLvector(FatJet_pt[1],FatJet_eta[1],FatJet_phi[1],FatJet_msoftdrop[1])")
a.SetVar("mtt","analyzer::invariantMass(lead_vect,sublead_vect)")
a.SetVar("deltaY","abs(lead_vect->Rapidity()-sublead_vect->Rapidity())")
a.SetVar("nBtags","analyzer::subjet_btag(FatJet_subJetIdx1[0],FatJet_subJetIdx2[0],SubJet_btagCSVV2) + analyzer::subjet_btag(FatJet_subJetIdx1[1],FatJet_subJetIdx2[1],SubJet_btagCSVV2)")
if not a.isData: norm = (xsec*lumi)/a.genEventCount
else: norm = 1.

presel = a.Cut()

yLow_b0 = a.Cut({"yLow_b0":"deltaY < 1.0 && nBtags == 0"},presel)
yLow_b1 = a.Cut({"yLow_b1":"deltaY < 1.0 && nBtags == 1"},presel)
yLow_b2 = a.Cut({"yLow_b2":"deltaY < 1.0 && nBtags == 2"},presel)
yHigh_b0 = a.Cut({"yHigh_b0":"deltaY > 1.0 && nBtags == 0"},presel)
yHigh_b1 = a.Cut({"yHigh_b1":"deltaY > 1.0 && nBtags == 1"},presel)
yHigh_b2 = a.Cut({"yHigh_b2":"deltaY > 1.0 && nBtags == 2"},presel)

out_f = ROOT.TFile(options.output,"RECREATE")
out_f.cd()

h_presel = presel.Histo1D(("presel","presel",30 ,0 ,6000),'mtt')
h_yLow_b0 = yLow_b0.Histo1D(("yLow_b0","yLow_b0",30 ,0 ,6000),'mtt')
h_yLow_b1 = yLow_b1.Histo1D(("yLow_b1","yLow_b1",30 ,0 ,6000),'mtt')
h_yLow_b2 = yLow_b2.Histo1D(("yLow_b2","yLow_b2",30 ,0 ,6000),'mtt')
h_yHigh_b0 = yHigh_b0.Histo1D(("yHigh_b0","yHigh_b0",30 ,0 ,6000),'mtt')
h_yHigh_b1 = yHigh_b1.Histo1D(("yHigh_b1","yHigh_b1",30 ,0 ,6000),'mtt')
h_yHigh_b2 = yHigh_b2.Histo1D(("yHigh_b2","yHigh_b2",30 ,0 ,6000),'mtt')

for h in [h_presel,h_yLow_b0,h_yLow_b1,h_yLow_b2,h_yHigh_b0,h_yHigh_b1,h_yHigh_b2]: h.Scale(norm)

norm_hist = ROOT.TH1F('norm','norm',1,0,1)
norm_hist.SetBinContent(1,norm)
norm_hist.Write()

h_presel.Write()
h_yLow_b0.Write()
h_yLow_b1.Write()
h_yLow_b2.Write()
h_yHigh_b0.Write()
h_yHigh_b1.Write()
h_yHigh_b2.Write()

out_f.Close()

print("Total time: "+str((time.time()-start_time)/60.) + ' min')
