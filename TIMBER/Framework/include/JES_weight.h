#ifndef _TIMBER_JES_WEIGHT
#define _TIMBER_JES_WEIGHT
// Requires CMSSW
#include <string>
#include <vector>
#include "CondFormats/JetMETObjects/interface/JetCorrectorParameters.h"
#include "CondFormats/JetMETObjects/interface/FactorizedJetCorrector.h"
#include "CondFormats/JetMETObjects/interface/JetCorrectionUncertainty.h"
#include <ROOT/RVec.hxx>
#include "JetRecalibrator.h"
#include "common.h"

using namespace ROOT::VecOps;

class JES_weight {
    private:
        const std::string _jesTag, _jetType, _uncertType;
        const bool _redoJECs;

    public:
        JetRecalibrator _jetRecalib;
        JES_weight(str jesTag, str jetType, str uncertType = "", bool redoJECs=false);
        ~JES_weight(){};

        bool check_type_exists();
        std::vector<std::string> get_sources();

        template <class T>
        RVec< RVec<float> > eval(std::vector<T> jets, float fixedGridRhoFastjetAll){
            RVec< RVec<float> > out (jets.size());

            for (size_t ijet = 0; ijet < jets.size(); ijet++) {
                RVec<float> ijet_out {1.0, 1.0, 1.0};
            
                if (_redoJECs) {
                    float raw = 1.0 - jets[ijet].rawFactor;
                    _jetRecalib.SetCorrection(jets[ijet], fixedGridRhoFastjetAll);
                    _jetRecalib.SetUncertainty(jets[ijet], fixedGridRhoFastjetAll);

                    ijet_out[0] = raw * (_jetRecalib.GetCorrection());
                    ijet_out[1] = raw * (_jetRecalib.GetCorrection()+_jetRecalib.GetUncertainty());
                    ijet_out[2] = raw * (_jetRecalib.GetCorrection()-_jetRecalib.GetUncertainty());
                } else {
                    _jetRecalib.SetUncertainty(jets[ijet], fixedGridRhoFastjetAll);
                    ijet_out[1] = 1+_jetRecalib.GetUncertainty();
                    ijet_out[2] = 1+_jetRecalib.GetUncertainty();
                }
                out[ijet] = ijet_out;
            }
            return out;
        };
};
#endif