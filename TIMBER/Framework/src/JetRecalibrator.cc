#include "../include/JetRecalibrator.h"

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
    _L1JetPar = JetCorrectorParameters(
        _jecPath+"/"+globalTag+"_L1FastJet_"+jetFlavour+".txt", "");
    vJCP vPar {_L1JetPar};

    if (_upToLevel >= 2) {
        _L2JetPar = JetCorrectorParameters(
            _jecPath+"/"+globalTag+"_L2Relative_"+jetFlavour+".txt", "");
        vPar.push_back(_L2JetPar);
    }

    if (_upToLevel >= 3) {
        _L3JetPar = JetCorrectorParameters(
            _jecPath+"/"+globalTag+"_L3Absolute_"+jetFlavour+".txt", "");
        vPar.push_back(_L3JetPar);
    }
    // Add residuals if needed
    if (doResidualJECs) {
        _ResJetPar = JetCorrectorParameters(
            _jecPath+"/"+globalTag+"_L2L3Residual_"+jetFlavour+".txt");
        vPar.push_back(_ResJetPar);
    }
    // Construct FactorizedJetCorrector JetCorrectionUncertinaty objects
    FactorizedJetCorrector _JetCorrector (vPar);
    str filename = _jecPath+"/"+globalTag+"_Uncertainty_"+jetFlavour+".txt";
    JetCorrectionUncertainty _JetUncertainty (
            _jecPath+"/"+globalTag+"_Uncertainty_"+jetFlavour+".txt");

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

JetRecalibrator::~JetRecalibrator()
{
}

template <typename T>
void JetRecalibrator::SetCorrection(T jet, float rho) {
    _JetCorrector.setJetPhi(jet.phi);
    _JetCorrector.setJetEta(jet.eta);
    _JetCorrector.setJetPt(jet.pt * (1. - jet.rawFactor));
    _JetCorrector.setJetA(jet.area);
    _JetCorrector.setRho(rho);
    _correction = _JetCorrector.getCorrection();
};

template <typename T>
void JetRecalibrator::SetUncert(T jet, float rho, float delta) {
    if (delta != 0) {
        _JetUncertainty.setJetPhi(jet.phi);
        _JetUncertainty.setJetEta(jet.eta);
        _JetUncertainty.setJetPt(_correction * jet.pt * (1.0 - jet.rawFactor));
        _uncertainty = _JetUncertainty.getUncertainty(true);

        // variation[1] = _correction * std::max(0, 1+delta*uncertainty);
        // variation[2] = _correction * std::max(0, 1-delta*uncertainty);
    } else {
        _uncertainty = 0;
    }

};

template <typename T>
rvec_f JetRecalibrator::Correct(T jet, float rho, float delta) {
    rvec_f out = {jet.pt, jet.mass};
    float raw = 1.0 - jet.rawFactor;
    float correction = this->GetCorrection(jet, rho, delta);
    if (correction > 0) {
        out = {jet.pt*raw*correction, jet.mass*raw*correction};
    }

    return out;
}
