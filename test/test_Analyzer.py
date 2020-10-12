import ROOT
ROOT.gROOT.SetBatch(True)
from TIMBER.Analyzer import *
from TIMBER.Tools.Common import CompileCpp

class TestAnalyzer():
    def setup(self):
        CompileCpp('TIMBER/Framework/include/common.h') # Compile (via gInterpreter) commonly used c++ code
        CompileCpp('examples/example.cc')
        self.a = analyzer('examples/GluGluToHToTauTau.root')
        self.a.Cut("test_cut1", "Jet_pt.size() > 0")
        self.a.Define('lead_vector', 'analyzer::TLvector(Jet_pt[0],Jet_eta[0],Jet_phi[0],Jet_mass[0])')
        self.a.Define('sublead_vector','analyzer::TLvector(Jet_pt[1],Jet_eta[1],Jet_phi[1],Jet_mass[1])')
        self.a.Define('invariantMass','analyzer::invariantMass(lead_vector,sublead_vector)')

    def test_genEventCount_None(self):
        '''Test genEventCount is assigned 0 when branch doesn't exist in test file'''
        assert self.a.genEventCount == 0

    def test_lhaid_None(self):
        '''Test lhaid is assigned 0 when branch doesn't exist in test file'''
        assert self.a.lhaid == '-1'

    def test_GetTrackedNodeNames(self):
        '''Test GetTrackNodeNames method after adding a node'''
        assert self.a.GetTrackedNodeNames() == ['test_cut1','lead_vector','sublead_vector','invariantMass']

    def test_makehist(self):
        '''Makes a simple histogram of the defined variable'''
        h = self.a.DataFrame.Histo1D(('m_jj','m_{jj}',20,0,200),'invariantMass')
        h.Draw("lego")
        assert True

    def test_snapshot(self,tmp_path):
        '''Makes a simple snapshot'''
        out_vars = ['nJet','test_define']
        self.a.GetActiveNode().Snapshot(out_vars,str(tmp_path)+'/ex1_out.root','test_snapshot',lazy=False,openOption='RECREATE') 
        assert True

    def test_AddCorrection(self):
        pass

    def test_MakeWeightCols(self):
        pass

    def test_MakeTemplateHistos(self):
        pass

    def test_DrawTemplates(self):
        pass

    def test_Nminus1(self):
        pass

    def test_PrintNodeTree(self):
        pass

def test_Groups():
    a = analyzer('examples/GluGluToHToTauTau.root')
    CompileCpp('TIMBER/Framework/include/common.h') # Compile (via gInterpreter) commonly used c++ code
    CompileCpp('examples/example.cc')
    
    test_vg = VarGroup('test_vg')
    test_vg.Add('lead_vector', 'analyzer::TLvector(Jet_pt[0],Jet_eta[0],Jet_phi[0],Jet_mass[0])')
    test_vg.Add('sublead_vector','analyzer::TLvector(Jet_pt[1],Jet_eta[1],Jet_phi[1],Jet_mass[1])')
    test_vg.Add('invariantMass','analyzer::invariantMass(lead_vector,sublead_vector)')
    
    test_cg = CutGroup('test_cg')
    test_cg.Add("test_cut1", "Jet_pt.size() > 0")
    
    a.Apply([test_vg, test_cg])
    rep = a.DataFrame.Report()
    rep.Print()
