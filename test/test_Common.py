from TIMBER.Analyzer import analyzer
from TIMBER.Tools.Common import CompileCpp

class CommonTest():
    def setup(self):
        self.a = analyzer('examples/GluGluToHToTauTau.root')

    def test_CutflowHist(self):
        pass

    def test_CutflowTxt(self):
        pass

    def test_openJSON(self):
        pass

    def test_GetHistBinningTuple(self):
        pass