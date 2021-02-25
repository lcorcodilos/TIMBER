#include "../include/JetRecalibrator.h"

JetRecalibrator::JetRecalibrator(): _globalTag(''), _jetFlavour(''),_doResidualJECs(true),_upToLevel(3){};

JetRecalibrator::JetRecalibrator(str globalTag, str jetFlavour, bool doResidualJECs,
                                 str jecPath, int upToLevel)://,
                                //  bool calculateSeparateCorrections,
                                //  bool calculateType1METCorrection,
                                //  std::map<str, float> type1METParams):
    _globalTag{globalTag}, _jetFlavour{jetFlavour}, _doResidualJECs{doResidualJECs},
    _jecPath{jecPath}, _upToLevel{upToLevel}
//     _calculateSeparateCorrections{calculateSeparateCorrections},
//     _calculateType1METCorrection{calculateType1METCorrection}, _type1METParams{type1METParams}
{
    // Make base corrections
    paths = JMEpaths(_globalTag, _jetFlavour);

    _L1JetPar = paths.GetParameters("1");
    vJCP vPar {_L1JetPar};

    if (_upToLevel >= 2) {
        _L2JetPar = paths.GetParameters("2");;
        vPar.push_back(_L2JetPar);
    }

    if (_upToLevel >= 3) {
        _L3JetPar = paths.GetParameters("3");;
        vPar.push_back(_L3JetPar);
    }
    // Add residuals if needed
    if (doResidualJECs) {
        _ResJetPar = paths.GetParameters("Res");;
        vPar.push_back(_ResJetPar);
    }
    // Construct FactorizedJetCorrector JetCorrectionUncertinaty objects
    FactorizedJetCorrector _JetCorrector (vPar);
    str filename = paths.GetPath("Uncert");
    JetCorrectionUncertainty _JetUncertainty = paths.GetUncertainty();

    /* The following was converted from NanoAOD-tools but is not used (even in NanoAOD-tools)
        // if (boost::filesystem::exists(filename)) {
    //     JetCorrectionUncertainty _JetUncertainty (
    //         _jecPath+"/"+globalTag+"_Uncertainty_"+jetFlavour+".txt"
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
