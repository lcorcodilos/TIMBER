#include "../include/JetRecalibrator.h"

JetRecalibrator::JetRecalibrator(): _jecTag(""), _jetType(""),_doResidualJECs(true),_uncertType(""),_upToLevel(3){};

JetRecalibrator::JetRecalibrator(str jecTag, str jetType, bool doResidualJECs,
                                 str uncertType, int upToLevel)://,
                                //  bool calculateSeparateCorrections,
                                //  bool calculateType1METCorrection,
                                //  std::map<str, float> type1METParams):
    _jecTag{jecTag}, _jetType{jetType}, _doResidualJECs{doResidualJECs},
    _uncertType{uncertType}, _upToLevel{upToLevel}, _paths(_jecTag, _jetType)
//     _calculateSeparateCorrections{calculateSeparateCorrections},
//     _calculateType1METCorrection{calculateType1METCorrection}, _type1METParams{type1METParams}
{
    // Make base corrections
    JetCorrectorParameters L1JetPar = _paths.GetParameters("L1");
    vJCP vPar {L1JetPar};
    if (_upToLevel >= 2) {
        JetCorrectorParameters L2JetPar = _paths.GetParameters("L2");
        vPar.push_back(L2JetPar);
    }

    if (_upToLevel >= 3) {
        JetCorrectorParameters L3JetPar = _paths.GetParameters("L3");
        vPar.push_back(L3JetPar);
    }
    // Add residuals if needed
    if (doResidualJECs) {
        JetCorrectorParameters ResJetPar = _paths.GetParameters("Res");
        vPar.push_back(ResJetPar);
    }
    // Construct FactorizedJetCorrector JetCorrectionUncertinaty objects
    _JetCorrector = new FactorizedJetCorrector(vPar);
    _JetUncertainty = new JetCorrectionUncertainty(_paths.GetParameters("Uncert",uncertType));
    /* The following was converted from NanoAOD-tools but is not used (even in NanoAOD-tools)
    // str filename = _paths.GetPath("Uncert");
    // if (boost::filesystem::exists(filename)) {
    //     JetCorrectionUncertainty _JetUncertainty (
    //         _jecPath+"/"+jecTag+"_Uncertainty_"+jetType+".txt"
    //     );
    // } else {
    //     std::cout << "Missing JEC uncertainty file '"+filename+"', so jet energy uncertainties will not be available!" << std::endl;
    // }

    // Setup separate corrections
    std::map<str, FactorizedJetCorrector> separateJetCorrectors;
    if (_calculateSeparateCorrections || _calculateType1METCorrection){
        vJCP vParL1;
        vParL1.push_back(_L1JetPar);
        FactorizedJetCorrector separateJetCorrectors["L1"] (vParL1);
        if (_upToLevel >= 2 && _calculateSeparateCorrections) {
            vJCP vParL2;
            vParL2.push_back(_L1JetPar);
            vParL2.push_back(_L2JetPar);
            separateJetCorrectors["L1L2"] = FactorizedJetCorrector(vParL2);
        }
        if (_upToLevel >= 3 && _calculateSeparateCorrections) {
            vJCP vParL3;
            vParL3.push_back(_L1JetPar);
            vParL3.push_back(_L2JetPar);
            vParL3.push_back(_L3JetPar);
            separateJetCorrectors["L1L2L3"] = FactorizedJetCorrector(vParL3);
        }
        if (_doResidualJECs && _calculateSeparateCorrections) {
            vJCP vParL3Res;
            vParL3Res.push_back(_L1JetPar);
            vParL3Res.push_back(_L2JetPar);
            vParL3Res.push_back(_L3JetPar);
            vParL3Res.push_back(_ResJetPar);
            separateJetCorrectors = FactorizedJetCorrector(vParL3Res);
        }
    }
    */
}

JetRecalibrator::~JetRecalibrator(){
    delete _JetCorrector;
}