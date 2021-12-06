import ROOT
from TIMBER.Analyzer import TIMBERPATH, Correction
from TIMBER.Tools.Common import GetPUfile

def AutoPU(a, year, ULflag=True):
    '''Automatically perform the standard pileup calculation on the analyzer object.

    @param a (analyzer): Object to manipulate and return.
    @param year (str): 2016, 2016APV, 2017, 2018
    @param ULflag (bool): Set to True for UL. Defaults to True.

    Returns:
        analyzer: Manipulated input.
    '''
    autoPU = MakePU(a, year, ULflag)
    print ('AutoPU: Extracting Pileup_nTrueInt distribution')
    ROOT.gROOT.cd()
    ROOT.gDirectory.Add(autoPU.GetValue())
    data_files = GetPUfilesStr(year,ULflag=ULflag)
    c_PU = Correction('Pileup','TIMBER/Framework/src/Pileup_weight.cc',[data_files], corrtype="weight")
    a.AddCorrection(c_PU)
    return a

def MakePU(a, year, ULflag=True, filename=''):
    '''Create the histogram for the "Pileup_nTrueInt" distribution.
    Histogram will be named "autoPU".

    @param a (analyzer): Object to manipulate and return.
    @param year (str): 2016, 2016APV, 2017, 2018
    @param ULflag (bool): Set to True for UL. Defaults to True.
    @param filename (str): Name of ROOT file to save pileup histogram to.
        Defaults to '' in which case no file will be written.

    Returns:
        TH1F: Histogram of Pileup_nTrueInt.
    '''
    ftemplate = ROOT.TFile.Open(TIMBERPATH+"TIMBER/data/Pileup/"+GetPUfile(year,ULflag,'nominal'))
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

def ApplyPU(a, filename, year, ULflag=True, histname='autoPU'):
    '''Create the histogram for the "Pileup_nTrueInt" distribution.
    Histogram will be named "autoPU".

    @param a (analyzer): Object to manipulate and return.
    @param filename (str): Name of ROOT file to save pileup histogram to.
        Defaults to '' in which case no file will be written.
    @param year (str): 2016, 2016APV, 2017, 2018
    @param ULflag (bool): Set to True for UL. Defaults to True.
    @param histname (str): Histogram name in the file. Defaults to 'autoPU'.

    Returns:
        TH1F: Histogram of Pileup_nTrueInt.
    '''
    data_files = GetPUfilesStr(year,ULflag=ULflag)
    c_PU = Correction('Pileup','TIMBER/Framework/include/Pileup_weight.h',
                      [filename, data_files,
                       histname, 'pileup'],
                       corrtype="weight")
    a.AddCorrection(c_PU)
    return a

def GetPUfilesStr(year,ULflag=True):
    '''Creates the input string for the Pileup_weight correction module.
    Final output is a python string representing the C++ vector of strings
    to each of the pileup files of interest, ordered as nominal, up, and down.

    Args:
        year (str): 2016, 2016APV, 2017, 2018
        ULflag (bool, optional): Defaults to True.

    Returns:
        str: String formated for the Pileup_weight correction module.
    '''
    data_files = [GetPUfile(year,ULflag,variation) for variation in ['nominal','up','down']]
    data_files = '{"'+'","'.join(data_files)+'"}'
    return data_files
