'''@addtogroup AutoJME AutoJME tool (AutoJME.py)
Automatic calculation of JES, JER, JMS, and JMR factors and uncertainties
per-jet per-event and calibration of \f$p_{T}\f$ and mass with associated
variations performed as well.
@{
'''

from TIMBER.Tools.Common import GetJMETag, _year_to_thousands_str
from TIMBER.Analyzer import Calibration

AK8collection = "FatJet"
AK4collection = "Jet"

def AutoJME(a, jetCollection, year, dataEra='',ULflag=True):
    '''NOTE: The AK4 corrections are untested and may not work as intended. If you are interested
    in implementing these, please feel free to make a Pull Request!
    
    Automatic calculation of JES, JER, JMS, and JMR factors and uncertainties
    per-jet per-event. Note that no calibration of \f$p_{T}\f$ and mass is performed
    but some commented-out lines are left to show how this might be done if the per-jet
    values are not desired. Otherwise, it is recommended to manually define how the pt
    or mass changes via `analyzer.Define()` since many analyses do not do the same thing.

    If you're looking for a recipe, in general, one wants to...
    
    - For MC FatJets (AK8s), apply JES and JER to the \f$p_{T}\f$ and JES, JER, JMS, and JMR to the mass.
    - For MC Jets (AK4s), apply JES and JER to the \f$p_{T}\f$.
    - For data, only recalibrate the jets for the new JECs.

    @param a (analyzer): TIMBER analyzer object which will be manipulated and returned.
    @param jetCollection (str): FatJet or Jet. Note that if you have a custom collection built from either of these,
        you may change the values of the `AK8collection` and/or `AK4collection` attributes of the AutoJME.py namespace
        to other values.
    @param year (str): 2016, 2016APV, 2017, 2018
    @param dataEra (str, optional): If providing data, include the "era" (A or B or C, etc). Defaults to ''.
    @param ULflag (bool, optional): Defaults to True.

    Raises:
        ValueError: Provided jet collection is not "FatJet" or "Jet"

    Returns:
        analyzer: Manipulated version of the input analyzer object.
    '''
    year = _year_to_thousands_str(year)
    dataEraLetter = dataEra.lower().replace('data','').upper().replace('1','').replace('2','')
    if jetCollection == AK8collection:
        jetType = "AK8PFPuppi"
        genJetColl = "GenJetAK8"
        doMass = True
    elif jetCollection == AK4collection:
        jetType = "AK4PFCHS"
        genJetColl = "GenJet"
        doMass = False
    else:
        raise ValueError("Jet collection name `%s` not supported. Only FatJet or Jet."%jetCollection)
    
    if not a.isData:
        jes_tag = GetJMETag("JES",year,"MC",ULflag)
        jes = Calibration("%s_JES"%jetCollection,"TIMBER/Framework/include/JES_weight.h",
                [jes_tag,jetType,"",True], corrtype="Calibration")

        jer_tag = GetJMETag("JER",year,"MC",ULflag)
        jer = Calibration("%s_JER"%jetCollection,"TIMBER/Framework/include/JER_weight.h",
                [jer_tag,jetType], corrtype="Calibration")
        if doMass:
            jms = Calibration("%s_JMS"%jetCollection,"TIMBER/Framework/include/JMS_weight.h",
                    [int(year.replace('APV',''))], corrtype="Calibration")
            jmr = Calibration("%s_JMR"%jetCollection,"TIMBER/Framework/include/JMR_weight.h",
                    [int(year.replace('APV',''))], corrtype="Calibration")

        # calibdict = {"%s_pt"%jetCollection:[jes,jer],"%s_mass"%jetCollection:[jes,jer,jms,jmr]}
        evalargs = {
            jes: {"jets":"%ss"%jetCollection,"rho":"fixedGridRhoFastjetAll"},
            jer: {"jets":"%ss"%jetCollection,"genJets":"%ss"%genJetColl},
            jms: {"nJets":"n%s"%jetCollection},
            jmr: {"jets":"%ss"%jetCollection,"genJets":"%ss"%genJetColl}
        }
    else:
        jes_tag = GetJMETag("JES",year,dataEraLetter,ULflag)
        jes = Calibration("%s_JES"%jetCollection,"TIMBER/Framework/include/JES_weight.h",
                [jes_tag,jetType,"",True], corrtype="Calibration")
        
        # calibdict = {"%s_pt"%jetCollection:[jes],"%s_mass"%jetCollection:[jes]}
        evalargs = {
            jes: {"jets":"%ss"%jetCollection,"rho":"fixedGridRhoFastjetAll"}
        }
        
    # a.CalibrateVars(calibdict,evalargs,"Calibrated%s"%jetCollection,variationsFlag=(not a.isData))
    a.CalibrateVars({},evalargs,'',variationsFlag=(not a.isData))

    return a
## @}