import ROOT
from TIMBER.Analyzer import Correction, HistGroup, analyzer

ROOT.gROOT.SetBatch(True)

year = 17
setname = 'Zprime2000'

trigDict = {
    16: ['HLT_PFHT900','HLT_PFHT800','HLT_PFJet450'],
    17: ['HLT_PFHT1050','HLT_PFJet500'],
    18: ['HLT_PFHT1050','HLT_PFJet500']
}

topTag = {
    16: 0.632,
    17: 0.554,
    18: 0.685
}

a = analyzer('../../ZprimeToTT_M2000_W20_RunIIAutumn18NanoAODv7.root') # open file

c_PDF = Correction('PDF','TIMBER/Framework/include/PDFweight_uncert.h', constructor=[a.lhaid],
                    mainFunc='eval', corrtype='uncert')
c_Tpt = Correction('TptReweight','TIMBER/Framework/include/TopPt_weight.h', constructor=[],
                    mainFunc='eval', corrtype='weight')
c_Prefire = Correction('Prefire','TIMBER/Framework/include/Prefire_weight.h', constructor=[year],
                    mainFunc='eval', corrtype='weight') # use 17 for now until we can check year
c_HEM = Correction('HEM','TIMBER/Framework/include/HEM_drop.h', constructor=[setname],
                    mainFunc='eval', corrtype='corr')
c_TopTag1 = Correction('TopTag1','TIMBER/Framework/include/TopTagDAK8_SF.h', constructor=[year,"0p5",True],
                    mainFunc='eval', corrtype='weight')
c_TopTag0 = c_TopTag1.Clone('TopTag0')

a.Cut('trigger',a.GetTriggerString(trigDict[year]))
a.Cut('Flags',a.GetFlagString())
a.Cut('numberFatJets','nFatJet>1')
a.Cut('pt','FatJet_pt[0] > 400 && FatJet_pt[1] > 400') # will seg fault if nFatJet<=1 !!
a.Cut('eta','abs(FatJet_eta[0]) < 2.4 && abs(FatJet_eta[1]) < 2.4')
a.Cut('oppositeHemis','hardware::DeltaPhi(FatJet_phi[0], FatJet_phi[1]) > M_PI/2')
a.Cut('massLead','FatJet_msoftdrop[0] > 105 && FatJet_msoftdrop[0] < 210')
a.Cut('massSublead','FatJet_msoftdrop[1] > 105 && FatJet_msoftdrop[1] < 210')
a.Define('FatJet_vect','hardware::TLvector(FatJet_pt, FatJet_eta, FatJet_phi, FatJet_msoftdrop)')
a.Define('mtt','hardware::InvariantMass({FatJet_vect[0], FatJet_vect[1]})')
a.Cut('DAK8_sublead','FatJet_deepTagMD_TvsQCD[1] > %s'%topTag[year])
a.Define('GenPart_vect','hardware::TLvector(GenPart_pt, GenPart_eta, GenPart_phi, GenPart_mass)')

a.AddCorrection(c_PDF)
a.AddCorrection(c_Tpt, evalArgs={'jet0':'FatJet_vect[0]','jet1':'FatJet_vect[1]'})
a.AddCorrection(c_Prefire)
a.AddCorrection(c_HEM)
presel = a.AddCorrection(c_TopTag1,evalArgs={"pt":"FatJet_pt[1]"})

# Signal region
a.Cut('DAK8_lead','FatJet_deepTagMD_TvsQCD[0] > %s'%topTag[year])
a.AddCorrection(c_TopTag0,evalArgs={"pt":"FatJet_pt[0]"})
a.MakeWeightCols(correlations=[('TopTag0','TopTag1')]) 
SR_hists = a.MakeTemplateHistos(ROOT.TH1F('SR_mtt','Invariant mass in signal region',30,1000,4000),'mtt',lazy=True)
# Go back to do CR
a.SetActiveNode(presel)
a.Cut('NotDAK8_lead','FatJet_deepTagMD_TvsQCD[0] < %s'%topTag[year])
a.MakeWeightCols()
CR_hists = a.MakeTemplateHistos(ROOT.TH1F('CR_mtt','Invariant mass in control region',30,1000,4000),'mtt',lazy=False)

a.PrintNodeTree('test.dot',verbose=True)

out = ROOT.TFile.Open('exercise5.root','RECREATE')
out.cd()
SR_hists.Do('Write')
CR_hists.Do('Write')
out.Close()

a.DrawTemplates(SR_hists,'plots/')
a.DrawTemplates(CR_hists,'plots/')