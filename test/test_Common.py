from TIMBER.Analyzer import analyzer
from TIMBER.Tools.Common import *

class CommonTest():
    @classmethod
    def setup_class(cls):
        cls.a = analyzer('examples/GluGluToHToTauTau.root')

    def test_CutflowHist(self):
        pass

    def test_CutflowTxt(self):
        pass

    def test_OpenJSON(self):
        assert OpenJSON('test.json') == {
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
        h3 = ROOT.TH2F('testH2','',10,0,10,20,0,20,30,0,30)
        binning,dim = GetHistBinningTuple(h3)
        assert binning == (10,0,10,20,0,20,30,0,30)
        assert dim == 3
        pass