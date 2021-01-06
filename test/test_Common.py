from TIMBER.Analyzer import analyzer
from TIMBER.Tools.Common import *

class TestCommon():
    @classmethod
    def setup_class(cls):
        cls.a = analyzer('examples/GluGluToHToTauTau.root')
        cls.a.Cut("test_cut1", "Jet_pt.size() > 0")
        # cls.a.Cut('test_cut2','Jet_pt[0] > 50')

    def test_CutflowHist(self):
        CutflowHist('test_cutflow',self.a.GetActiveNode())

    def test_CutflowTxt(self):
        CutflowTxt('test_cutflow.txt',self.a.GetActiveNode())

    def test_OpenJSON(self):
        assert OpenJSON('test/test.json') == {
            "test1": 1,
            "test2": {
                "float": 1.0,
                "str": "string",
                "list": []
            }
        }
        pass

    def test_GetHistBinningTuple(self):
        h = ROOT.TH1F('testH','',10,0,10)
        binning,dim = GetHistBinningTuple(h)
        assert binning == (10,0,10)
        assert dim == 1
        h2 = ROOT.TH2F('testH2','',10,0,10,20,0,20)
        binning,dim = GetHistBinningTuple(h2)
        assert binning == (10,0,10,20,0,20)
        assert dim == 2
        h3 = ROOT.TH3F('testH3','',10,0,10,20,0,20,30,0,30)
        binning,dim = GetHistBinningTuple(h3)
        assert binning == (10,0,10,20,0,20,30,0,30)
        assert dim == 3
        pass