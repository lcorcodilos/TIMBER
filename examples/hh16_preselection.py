import ROOT
ROOT.ROOT.EnableImplicitMT(4)

import time, os
from optparse import OptionParser
from collections import OrderedDict

from JHUanalyzer.Analyzer.analyzer import analyzer, Group, VarGroup, CutGroup
from JHUanalyzer.Tools.Common import openJSON,CutflowHist
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

# Initialize
a = analyzer(options.input)

# Example of how to calculate MC normalization for luminosity
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
if not a.isData: norm = (xsec*lumi)/a.genEventCount
else: norm = 1.

# Load in C functions (common and custom)
a.SetCFunc(commonc.vector) # common library
a.SetCFunc(commonc.invariantMass) # common library
customc.Import("pdfweights","JHUanalyzer/Corrections/pdfweights.cc") # "extra"/custom library 
# a.SetCFunc(customc.pdfweights)

# Start an initial group of cuts
preselection1 = CutGroup('preselection1')
if '16' in options.output: preselection1.Add("triggers","(HLT_PFHT800||HLT_PFHT900||HLT_AK8PFJet360_TrimMass30)")
else: preselection1.Add("triggers","(HLT_PFHT1050||HLT_AK8PFJet400_TrimMass30)")
preselection1.Add("nFatJets","nFatJet > 1")
preselection1.Add("pt0","FatJet_pt[0] > 300")
preselection1.Add("pt1","FatJet_pt[1] > 300")
preselection1.Add("eta0","abs(FatJet_eta[0]) < 2.4")
preselection1.Add("eta1","abs(FatJet_eta[1]) < 2.4")
preselection1.Add("jetID","((FatJet_jetId[0] & 2) == 2) && ((FatJet_jetId[1] & 2) == 2)")
preselection1.Add("PV","PV_npvsGood > 0")
preselection1.Add("deltaEta","abs(FatJet_eta[0] - FatJet_eta[1]) < 1.3")
preselection1.Add("tau21","(FatJet_tau2[0]/FatJet_tau1[0] < 0.55) && (FatJet_tau2[1]/FatJet_tau1[1] < 0.55)")
preselection1.Add("msoftdrop_1","105 < FatJet_msoftdrop[1] && FatJet_msoftdrop[1] < 135")

# Calculate some new comlumns that we'd like to cut on
newcolumns = VarGroup("newcolumns")
newcolumns.Add("lead_vect","analyzer::TLvector(FatJet_pt[0],FatJet_eta[0],FatJet_phi[0],FatJet_msoftdrop[0])")
newcolumns.Add("sublead_vect","analyzer::TLvector(FatJet_pt[1],FatJet_eta[1],FatJet_phi[1],FatJet_msoftdrop[1])")
newcolumns.Add("mhh","analyzer::invariantMass(lead_vect,sublead_vect)")
newcolumns.Add("mreduced","mhh - (FatJet_msoftdrop[0]-125.0) - (FatJet_msoftdrop[1]-125.0)")

# Cut on new column
preselection2 = CutGroup('preselection2')
preselection2.Add("cut_mreduced","mreduced > 750.")

# Perform final column calculations (done last after selection to save on CPU time)
newcolumns2 = VarGroup("newcolumns2")
newcolumns2.Add("mh","FatJet_msoftdrop[0]")
if not a.isData:
    newcolumns2.Add("Pdfweight",'analyzer::PDFweight(LHEPdfWeight)')
    newcolumns2.Add("Pdfweight_up",'Pdfweight[0]')
    newcolumns2.Add("Pdfweight_down",'Pdfweight[1]')
newcolumns2.Add("SRTT","FatJet_btagHbb[0] > 0.8 && FatJet_btagHbb[1] > 0.8")
newcolumns2.Add("SRLL","FatJet_btagHbb[0] > 0.3 && FatJet_btagHbb[1] > 0.3 && (!SRTT)")
newcolumns2.Add("ATTT","(FatJet_btagHbb[0] > 0.8 && FatJet_btagHbb[1] < 0.3) || (FatJet_btagHbb[1] > 0.8 && FatJet_btagHbb[0] < 0.3)")
newcolumns2.Add("ATLL","(FatJet_btagHbb[0] > 0.3 && FatJet_btagHbb[0] < 0.8 && FatJet_btagHbb[1] < 0.3) || (FatJet_btagHbb[1] > 0.3 && FatJet_btagHbb[1] < 0.8 && FatJet_btagHbb[0] < 0.3)")

# Apply all groups in list order to the base RDF loaded in during analyzer() initialization
preselected = a.Apply([preselection1,newcolumns,preselection2,newcolumns2])

# Since four analysis regions are covered with relatively complicated cuts to define them, a manual forking is simplest though a Disrcriminate function does exist for when you need to keep pass and fail of a selection
SRTT = preselected.Cut("SRTT","SRTT==1")
ATTT = preselected.Cut("ATTT","ATTT==1")
SRLL = preselected.Cut("SRLL","SRLL==1")
ATLL = preselected.Cut("ATLL","ATLL==1")

# Snapshot the tree for later
preselected.Snapshot("SR.*|AT.*|mh|mreduced|mhh|nFatJet|FatJet_pt",'snapshot_example.root',treename='preselected',lazy=True)

# Make some initial histograms and book file to save to
out_f = ROOT.TFile(options.output,"RECREATE")
out_f.cd()

print("Outfile booked")

# Need to call DataFrame attribute since Histo2D is a method of RDataFrame - this means at any point, you have access to the plain RDataFrame object corresponding to each node!
hists = [SRTT.DataFrame.Histo2D(("SRTT","SRTT",9 ,40 ,220 ,28 ,700 ,3500),'mh','mhh'),
ATTT.DataFrame.Histo2D(("ATTT","ATTT",9 ,40 ,220 ,28 ,700 ,3500),"mh","mhh"),
SRLL.DataFrame.Histo2D(("SRLL","SRLL",9 ,40 ,220 ,28 ,700 ,3500),"mh","mhh"),
ATLL.DataFrame.Histo2D(("ATLL","ATLL",9 ,40 ,220 ,28 ,700 ,3500),"mh","mhh")]

if not a.isData:
    extrahists = [SRTT.DataFrame.Histo2D(("SRTT_pdfUp","SRTT_pdfUp",9 ,40 ,220 ,28 ,700 ,3500),'mh','mhh','Pdfweight_up'),
    ATTT.DataFrame.Histo2D(("ATTT_pdfUp","ATTT_pdfUp",9 ,40 ,220 ,28 ,700 ,3500),"mh","mhh",'Pdfweight_up'),
    SRLL.DataFrame.Histo2D(("SRLL_pdfUp","SRLL_pdfUp",9 ,40 ,220 ,28 ,700 ,3500),"mh","mhh",'Pdfweight_up'),
    ATLL.DataFrame.Histo2D(("ATLL_pdfUp","ATLL_pdfUp",9 ,40 ,220 ,28 ,700 ,3500),"mh","mhh",'Pdfweight_up'),

    SRTT.DataFrame.Histo2D(("SRTT_pdfDown","SRTT_pdfDown",9 ,40 ,220 ,28 ,700 ,3500),'mh','mhh','Pdfweight_down'),
    ATTT.DataFrame.Histo2D(("ATTT_pdfDown","ATTT_pdfDown",9 ,40 ,220 ,28 ,700 ,3500),"mh","mhh",'Pdfweight_down'),
    SRLL.DataFrame.Histo2D(("SRLL_pdfDown","SRLL_pdfDown",9 ,40 ,220 ,28 ,700 ,3500),"mh","mhh",'Pdfweight_down'),
    ATLL.DataFrame.Histo2D(("ATLL_pdfDown","ATLL_pdfDown",9 ,40 ,220 ,28 ,700 ,3500),"mh","mhh",'Pdfweight_down')]

    hists.extend(extrahists)

norm_hist = ROOT.TH1F('norm','norm',1,0,1)
norm_hist.SetBinContent(1,norm)
norm_hist.Write()

for h in hists: 
    h.Scale(norm)
    h.Write()

# Draw a simple cutflow plot
# SRTT_cuts = preselection1+preselection2
# SRTT_cuts.Add("SRTT","SRTT==1")
SRTT_cutflow = CutflowHist('cutflow',SRTT) # SRTT.DataFrame already has the cuts and numbers, SRTT_cuts is just to name the histogram bins (but that means they must match up!)
SRTT_cutflow.Write()

# Cleanup
out_f.Close()
print("Total time: "+str((time.time()-start_time)/60.) + ' min')
