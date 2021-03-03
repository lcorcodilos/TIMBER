import ROOT, os
ROOT.gROOT.SetBatch(True)
from TIMBER.Analyzer import *
from TIMBER.Tools.Common import CompileCpp

class TestModules():
    @classmethod
    def setup_class(cls):
        cls.a = analyzer('examples/GluGluToHToTauTau.root')

    # EXAMPLE FILE DOES NOT HAVE GenPart or FatJet COLLECTIONS
    # COMMENTED OUT UNTIL A LATER TIME BUT WORKING AS OF Nov 13, 2020
    # def test_TopPt_weight(self):
    #     '''Test TopPt_weight module'''
    #     self.a.Cut('nJets','nJet > 1')
    #     self.a.Define('GenPart_vects','hardware::TLvector(GenPart_pt,GenPart_eta,GenPart_phi,GenPart_mass)')
    #     self.a.Define('Jet_vects','hardware::TLvector(Jet_pt,Jet_eta,Jet_phi,Jet_mass)')
    #     self.a.Define('Jet_pt0','Jet_pt[0]')
                
    #     c = Correction('TopPt','TIMBER/Framework/src/TopPt_weight.cc',mainFunc='corr',corrtype='corr')
    #     c_alpha = c.Clone('TopPt_alpha','alpha',newType='uncert')
    #     c_beta = c.Clone('TopPt_beta','beta',newType='uncert')
    #     self.a.AddCorrection(c,{'jet0':'Jet_vects[0]','jet1':'Jet_vects[1]'})
    #     self.a.AddCorrection(c_alpha,{'jet0':'Jet_vects[0]','jet1':'Jet_vects[1]','scale':'0.5'})
    #     self.a.AddCorrection(c_beta,{'jet0':'Jet_vects[0]','jet1':'Jet_vects[1]','scale':'0.5'})
    #     self.a.MakeWeightCols()

    #     htemplate = ROOT.TH1F('th1','',100,0,1000)
    #     hgroup = a.MakeTemplateHistos(htemplate,'Jet_pt0')
    #     a.Snapshot(['weight__.*'],'test_snapshot.root','Weights',lazy=False,openOption='RECREATE')
    #     a.DrawTemplates(hgroup, './')
    #     pass