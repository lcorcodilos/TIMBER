from TIMBER.Analyzer import analyzer
from TIMBER.Tools.Common import CompileCpp

class CommonTest():
    @classmethod
    def setup_class(cls):
        cls.a = analyzer('examples/GluGluToHToTauTau.root')

    def test_CutflowHist(self):
        pass

    def test_CutflowTxt(self):
        pass

    def test_openJSON(self):
        pass

    def test_GetHistBinningTuple(self):
        pass

    def test_StitchQCD(self):
        pass