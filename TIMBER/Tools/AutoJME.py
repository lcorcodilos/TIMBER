'''@addtogroup AutoJME AutoJME tool (AutoJME.py)
Automatic calculation of JES, JER, JMS, and JMR factors and uncertainties
per-jet per-event and calibration of \f$p_{T}\f$ and mass with associated
variations performed as well.
@{
'''

from TIMBER.Tools.Common import GetJMETag
from TIMBER.Analyzer import Calibration

def AutoJME(a, jetCollection, year, dataEra=''):
    '''Automatic calculation of JES, JER, JMS, and JMR factors and uncertainties
    per-jet per-event and calibration of \f$p_{T}\f$ and mass with associated
    variations performed as well.
    
    Apply standard JME modules to analyzer() object `a` for 
    a given jet collection, year, and data era (if a.isData).
    Output collection name will be called "Calibrated<jetCollection>"
    and will have the modified mass and pt and if MC, will have four possible variations
    of each variable for JES, JER, JMS, and JMR.

    For MC FatJets (AK8s), apply JES and JER to the \f$p_{T}\f$ and JES, JER, JMS, and JMR to the mass.
    For MC Jets (AK4s), apply JES and JER to the \f$p_{T}\f$.

    For data, only recalibrate the jets for the new JECs.

    @param a (analyzer): TIMBER analyzer object which will be manipulated and returned.
    @param jetCollection (str): FatJet or Jet.
    @param year (str): 2016, 2017, 2018, 2017UL, or 2018UL.
    @param dataEra (str, optional): If providing data, include the "era" (A or B or C, etc). Defaults to ''.

    Raises:
        ValueError: Provided jet collection is not "FatJet" or "Jet"

    Returns:
        analyzer: Manipulated version of the input analyzer object.
    '''
    dataEraLetter = dataEra.lower().replace('data','').upper().replace('1','').replace('2','')
    if jetCollection == "FatJet":
        jetType = "AK8PFPuppi"
        genJetColl = "GenJetAK8"
        doMass = True
    elif jetCollection == "Jet":
        jetType = "AK4PFCHS"
        genJetColl = "GenJet"
        doMass = False
    else:
        raise ValueError("Jet collection name `%s` not supported. Only FatJet or Jet."%jetCollection)
    
    if not a.isData:
        jes = Calibration("JES","TIMBER/Framework/include/JES_weight.h",
                [GetJMETag("JES",year,"MC"),jetType,"",True], corrtype="Calibration")
        jer = Calibration("JER","TIMBER/Framework/include/JER_weight.h",
                [GetJMETag("JER",year,"MC"),jetType], corrtype="Calibration")
        if doMass:
            jms = Calibration("JMS","TIMBER/Framework/include/JMS_weight.h",
                    [int(year.replace('UL',''))], corrtype="Calibration")
            jmr = Calibration("JMR","TIMBER/Framework/include/JMR_weight.h",
                    [int(year.replace('UL',''))], corrtype="Calibration")

        calibdict = {"%s_pt"%jetCollection:[jes,jer],"%s_mass"%jetCollection:[jes,jer,jms,jmr]}
        evalargs = {
            jes: {"jets":"%ss"%jetCollection,"rho":"fixedGridRhoFastjetAll"},
            jer: {"jets":"%ss"%jetCollection,"genJets":"%ss"%genJetColl},
            jms: {"nJets":"n%s"%jetCollection},
            jmr: {"jets":"%ss"%jetCollection,"genJets":"%ss"%genJetColl}
        }
    else:
        jes = Calibration("JES","TIMBER/Framework/include/JES_weight.h",
                [GetJMETag("JES",year,dataEraLetter),jetType,"",True], corrtype="Calibration")
        
        calibdict = {"%s_pt"%jetCollection:[jes],"%s_mass"%jetCollection:[jes]}
        evalargs = {
            jes: {"jets":"%ss"%jetCollection,"rho":"fixedGridRhoFastjetAll"}
        }
        
    a.CalibrateVars(calibdict,evalargs,"Calibrated%s"%jetCollection,variationsFlag=(not a.isData))

    return a
## @}