// Requires CMSSW
#include <string>
#include <vector>
#include "CondFormats/JetMETObjects/interface/JetCorrectorParameters.h"
#include "CondFormats/JetMETObjects/interface/FactorizedJetCorrector.h"
#include "CondFormats/JetMETObjects/interface/JetCorrectionUncertainty.h"
#include "JetRecalibrator.h"
#include "common.h"
#include "Pythonic.h"

class JES_weight {
    private:
        const std::string _globalTag, _jetFlavour, _uncertType;
        const bool _redoJECs;

    public:
        JetRecalibrator _jetRecalib;
        JES_weight(str globalTag, str jetFlavour, str uncertType = "", bool redoJECs=false);
        ~JES_weight(){};

        bool check_type_exists();
        std::vector<std::string> get_sources();

        template <class T>
        std::vector<float> eval(T jet, float rho){
            std::vector<float> out {1.0, 1.0, 1.0};

            if (_redoJECs) {
                _jetRecalib.SetCorrection(jet, rho);
                _jetRecalib.SetUncertainty(jet, rho);

                out[0] = _jetRecalib.GetCorrection();
                out[1] = _jetRecalib.GetCorrection()+_jetRecalib.GetUncertainty();
                out[2] = _jetRecalib.GetCorrection()-_jetRecalib.GetUncertainty();
            } else {
                _jetRecalib.SetUncertainty(jet, rho);
                out[1] = 1+_jetRecalib.GetUncertainty();
                out[2] = 1+_jetRecalib.GetUncertainty();
            }

            return out;
        };
};