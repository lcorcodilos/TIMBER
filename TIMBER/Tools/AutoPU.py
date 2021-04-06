import ROOT
from TIMBER.Analyzer import TIMBERPATH, Correction

def AutoPU(a, era):
    ftemplate = ROOT.TFile.Open(TIMBERPATH+'/TIMBER/data/Pileup/pileup_%s.root'%era)
    htemplate = ftemplate.Get('pileup')
    binning = ('autoPU','autoPU', htemplate.GetNbinsX(), htemplate.GetXaxis().GetXmin(), htemplate.GetXaxis().GetXmax())
    autoPU = a.DataFrame.Histo1D(binning,"Pileup_nTrueInt").GetValue()
    ROOT.gROOT.cd()
    ROOT.gDirectory.Add(autoPU)
    c_PU = Correction('pileup','TIMBER/Framework/src/Pileup_weight.cc',['"%s"'%era], corrtype="weight")
    a.AddCorrection(c_PU)
    ftemplate.Close()
    return a