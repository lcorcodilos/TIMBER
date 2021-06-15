import ROOT
from TIMBER.Analyzer import TIMBERPATH, Correction

def AutoPU(a, era):
    '''Automatically perform the standard pileup calculation on the analyzer object.

    @param a (analyzer): Object to manipulate and return.
    @param era (str): 2016(UL), 2017(UL), 2018(UL)

    Returns:
        analyzer: Manipulated input.
    '''
    autoPU = MakePU(a, era)
    print ('AutoPU: Extracting Pileup_nTrueInt distribution')
    ROOT.gROOT.cd()
    ROOT.gDirectory.Add(autoPU.GetValue())
    c_PU = Correction('Pileup','TIMBER/Framework/src/Pileup_weight.cc',[era], corrtype="weight")
    a.AddCorrection(c_PU)
    return a

def MakePU(a, era, filename=''):
    '''Create the histogram for the "Pileup_nTrueInt" distribution.
    Histogram will be named "autoPU".

    @param a (analyzer): Object to manipulate and return.
    @param era (str): 2016(UL), 2017(UL), 2018(UL)
    @param filename (str): Name of ROOT file to save pileup histogram to.
        Defaults to '' in which case no file will be written.

    Returns:
        TH1F: Histogram of Pileup_nTrueInt.
    '''
    ftemplate = ROOT.TFile.Open(TIMBERPATH+'/TIMBER/data/Pileup/pileup_%s.root'%era)
    htemplate = ftemplate.Get('pileup')
    binning = ('autoPU', 'autoPU', htemplate.GetNbinsX(), htemplate.GetXaxis().GetXmin(), htemplate.GetXaxis().GetXmax())
    autoPU = a.DataFrame.Histo1D(binning,"Pileup_nTrueInt")
    ftemplate.Close()
    if filename != '':
        fout = ROOT.TFile.Open(filename,'RECREATE')
        fout.cd()
        autoPU.Write()
        fout.Close()
    return autoPU

def ApplyPU(a, era, filename, histname='autoPU'):
    c_PU = Correction('Pileup','TIMBER/Framework/include/Pileup_weight.h',
                      [filename, 'pileup_%s'%era,
                       histname, 'pileup'],
                       corrtype="weight")
    a.AddCorrection(c_PU)
    return a