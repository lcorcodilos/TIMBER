#include <string>
#include <map>
#include <vector>
#include <algorithm>
#include <iostream>
// #include <boost/filesystem.hpp>
#include "Collection.h"
#include "JME_common.h"
#include <ROOT/RVec.hxx>
#include "CondFormats/JetMETObjects/interface/FactorizedJetCorrector.h"
#include "CondFormats/JetMETObjects/interface/JetCorrectorParameters.h"
#include "CondFormats/JetMETObjects/interface/JetCorrectionUncertainty.h"

typedef std::string str;
typedef ROOT::VecOps::RVec<float> rvec_f;
typedef std::vector<JetCorrectorParameters> vJCP;

class JetRecalibrator {
    private:
        str _jesTag, _jetFlavour, _uncertType;
        bool _doResidualJECs;//, _calculateSeparateCorrections, _calculateType1METCorrection;
        int _upToLevel;
        // std::map<str, float> _type1METParams;
        FactorizedJetCorrector _JetCorrector;
        float _correction;
        float _uncertainty;
        JetCorrectorParameters _L1JetPar, _L2JetPar, _L3JetPar, _ResJetPar;
        JetCorrectionUncertainty _JetUncertainty;

    public:
        JetRecalibrator(){};

        JetRecalibrator( str jesTag, str jetFlavour, bool doResidualJECs, str uncertType, int upToLevel=3
                        //  bool calculateSeparateCorrections=false,
                        //  bool calculateType1METCorrection=false,
                        //  std::map<str, float> type1METParams = {
                        //     {'jetPtThreshold', 15.},
                        //     {'skipEMfractionThreshold', 0.9},
                        //     {'skipMuons', 1} // True
                        //  }
                        );
        ~JetRecalibrator(){};

        // rho branch should be "fixedGridRhoFastjetAll"
        template <class T>
        void SetCorrection(T jet, float fixedGridRhoFastjetAll){
            _JetCorrector.setJetPhi(jet.phi);
            _JetCorrector.setJetEta(jet.eta);
            _JetCorrector.setJetPt(jet.pt * (1. - jet.rawFactor));
            _JetCorrector.setJetA(jet.area);
            _JetCorrector.setRho(fixedGridRhoFastjetAll);
            _correction = _JetCorrector.getCorrection();
        };

        template <class T>
        void SetUncertainty(T jet, float delta = 1){
            if (delta != 0) {
                _JetUncertainty.setJetPhi(jet.phi);
                _JetUncertainty.setJetEta(jet.eta);
                _JetUncertainty.setJetPt(_correction * jet.pt * (1.0 - jet.rawFactor));
                _uncertainty = delta*_JetUncertainty.getUncertainty(true);

            } else {
                _uncertainty = 0;
            }

        };

        float GetCorrection() {return _correction;};
        float GetUncertainty() {return _uncertainty;};

        template <class T>
        rvec_f Correct(T jet){
            rvec_f out = {jet.pt, jet.mass};
            float raw = 1.0 - jet.rawFactor;
            float correction = this->GetCorrection();
            if (correction > 0) {
                out = {jet.pt*raw*correction, jet.mass*raw*correction};
            }

            return out;
        };
};


