#include <string>
#include <map>
#include <vector>
#include <algorithm>
#include <iostream>
// #include <boost/filesystem.hpp>
#include "Collection.h"
#include <ROOT/RVec.hxx>
#include "CondFormats/JetMETObjects/interface/FactorizedJetCorrector.h"
#include "CondFormats/JetMETObjects/interface/JetCorrectorParameters.h"
#include "CondFormats/JetMETObjects/interface/JetCorrectionUncertainty.h"

typedef std::string str;
typedef ROOT::VecOps::RVec<float> rvec_f;
typedef std::vector<JetCorrectorParameters> vJCP;

class JetRecalibrator {
    private:
        const str _globalTag, _jetFlavour, _jecPath;
        const bool _doResidualJECs;//, _calculateSeparateCorrections, _calculateType1METCorrection;
        const int _upToLevel;
        // std::map<str, float> _type1METParams;
        FactorizedJetCorrector _JetCorrector;
        float _correction;
        float _uncertainty;
        JetCorrectorParameters _L1JetPar, _L2JetPar, _L3JetPar, _ResJetPar;
        JetCorrectionUncertainty _JetUncertainty;

    public:
        JetRecalibrator( str globalTag, str jetFlavour, bool doResidualJECs,
                        str jecPath, int upToLevel=3
                        //  bool calculateSeparateCorrections=false,
                        //  bool calculateType1METCorrection=false,
                        //  std::map<str, float> type1METParams = {
                        //     {'jetPtThreshold', 15.},
                        //     {'skipEMfractionThreshold', 0.9},
                        //     {'skipMuons', 1} // True
                        //  }
                        );
        ~JetRecalibrator();

        // rho branch should be "fixedGridRhoFastjetAll"
        template <typename T>
        void SetCorrection(T jet, float rho);
        template <typename T>
        void SetUncert(T jet, float rho, float delta = 0);

        float GetCorrection() {return _correction;};

        template <typename T>
        rvec_f Correct(T jet, float rho, float delta = 0);
};


