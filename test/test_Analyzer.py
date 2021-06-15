import ROOT, os
ROOT.gROOT.SetBatch(True)
from TIMBER.Analyzer import *
from TIMBER.Tools.Common import CompileCpp

class TestAnalyzer():
    @classmethod
    def setup_class(cls):
        CompileCpp('examples/example.cc')
        CompileCpp('test/test_weight.cc')
        cls.a = analyzer('examples/GluGluToHToTauTau.root')
        cls.a.Cut("test_cut1", "Jet_pt.size() > 0")
        cls.a.Define('lead_vector', 'hardware::TLvector(Jet_pt[0],Jet_eta[0],Jet_phi[0],Jet_mass[0])')
        cls.a.Define('sublead_vector','hardware::TLvector(Jet_pt[1],Jet_eta[1],Jet_phi[1],Jet_mass[1])')
        cls.a.Define('invariantMass','hardware::InvariantMass({lead_vector,sublead_vector})')

    def test_genEventSumw_None(self):
        '''Test genEventSumw is assigned 0 when branch doesn't exist in test file'''
        assert self.a.genEventSumw == 0

    def test_lhaid_None(self):
        '''Test lhaid is assigned 0 when branch doesn't exist in test file'''
        assert self.a.lhaid == -1

    def test_GetTrackedNodeNames(self):
        '''Test GetTrackNodeNames method after adding a node'''
        assert self.a.GetTrackedNodeNames() == ['base','test_cut1','lead_vector','sublead_vector','invariantMass']

    def test_makehist(self):
        '''Makes a simple histogram of the defined variable'''
        h = self.a.DataFrame.Histo1D(('m_jj','m_{jj}',20,0,200),'invariantMass')
        h.Draw("lego")
        assert True

    def test_range(self):
        '''Tests Range functionality'''
        bookmark = self.a.GetActiveNode()
        self.a.SetActiveNode(self.a.BaseNode)
        self.a.Range(0,1000,2)
        nevents = self.a.DataFrame.Count()
        self.a.SetActiveNode(bookmark)
        assert nevents.GetValue() == 500

    def test_snapshot(self):
        '''Makes a simple snapshot'''
        out_vars = ['nJet','test_define']
        self.a.GetActiveNode().Snapshot(out_vars,'test_out.root','test_snapshot',lazy=False,openOption='RECREATE') 
        assert True
    
    # No Runs tree in test file currently
    # def test_SaveRunChain(self):
    #     '''Save out RunChain'''
    #     self.a.SaveRunChain("test_out.root")
    #     assert True

    def test_Correction(self):
        c = Correction('test_weight','test/test_weight.cc')
        self.a.Define('Jet_pt0','Jet_pt[0]')
        self.a.AddCorrection(c,{'pt':'Jet_pt0'})
        self.a.MakeWeightCols()
        htemplate = ROOT.TH1F('th1','',100,0,1000)
        hgroup = self.a.MakeTemplateHistos(htemplate,'Jet_pt0')
        assert self.a.GetWeightName(c,'up','') == 'weight__test_weight_up'
        self.a.DrawTemplates(hgroup, './')

    def test_CommonVars(self):
        assert sorted(self.a.CommonVars(["Muon","Tau"])) == sorted(['phi', 'pt', 'charge', 'eta', 'mass', 'genPartIdx', 'jetIdx'])
        pass

    def test_MergeCollections(self):
        self.a.MergeCollections('Lepton',["Muon","Tau"])
        pass

    def test_SubCollection(self):
        self.a.SubCollection('Jet30','Jet','Jet_pt>30')
        pass

    def test_Nminus1(self):
        cgroup = CutGroup('Nminus1Test')
        cgroup.Add('cut1','Jet_eta[0] < 2.4 && Jet_eta[1] < 2.4')
        cgroup.Add('cut2','All(Muon_pt < 30)')
        cgroup.Add('cut3','Sum(Jet_btag > 0.5) > 1')
        self.a.Nminus1(cgroup)
        pass

    def test_PrintNodeTree(self):
        self.a.PrintNodeTree('test.pdf')
        pass

    def test_GetTriggerString(self):
        assert self.a.GetTriggerString(['HLT_IsoMu24','HLT_IsoMu24_eta2p1','NotReal']) == '((HLT_IsoMu24==1) || (HLT_IsoMu24_eta2p1==1))'
        pass

    def test_GetFlagString(self):
        assert self.a.GetFlagString(['HLT_IsoMu24','HLT_IsoMu24_eta2p1','NotReal']) == '((HLT_IsoMu24==1) && (HLT_IsoMu24_eta2p1==1))'
        pass

    def test_CollectionStruct(self):
        self.a.Cut('structCut','Jets[0].pt > 0')

def test_Groups():
    a = analyzer('examples/GluGluToHToTauTau.root')
    # CompileCpp('TIMBER/Framework/include/common.h') # Compile (via gInterpreter) commonly used c++ code
    # CompileCpp('examples/example.cc')
    
    test_vg = VarGroup('test_vg')
    test_vg.Add('lead_vector', 'hardware::TLvector(Jet_pt[0],Jet_eta[0],Jet_phi[0],Jet_mass[0])')
    test_vg.Add('sublead_vector','hardware::TLvector(Jet_pt[1],Jet_eta[1],Jet_phi[1],Jet_mass[1])')
    test_vg.Add('invariantMass','hardware::InvariantMass({lead_vector,sublead_vector})')
    
    test_cg = CutGroup('test_cg')
    test_cg.Add("test_cut1", "Jet_pt.size() > 0")
    
    a.Apply([test_vg, test_cg])
    rep = a.DataFrame.Report()
    rep.Print()

def test_CollectionGroup():
    a = analyzer('examples/GluGluToHToTauTau.root')
    assert ('Jet' in a.GetCollectionNames())
