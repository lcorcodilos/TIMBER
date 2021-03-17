#ifndef _TIMBER_JETRECALIBRATOR
#define _TIMBER_JETRECALIBRATOR
#include <string>
#include <map>
#include <vector>
#include <algorithm>
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
/**
 * @brief C++ class to recalibrate the \f$p_{T}\f$ of jets.
 *  Initialized with basic parameters and calculations done on vectors of jets from
 *  an event using the class methods.
 */
class JetRecalibrator {
    private:
        bool _doResidualJECs;//, _calculateSeparateCorrections, _calculateType1METCorrection;
        str _jecTag, _jetType, _uncertType;
        int _upToLevel;
        // std::map<str, float> _type1METParams;
        FactorizedJetCorrector* _JetCorrector;
        float _correction;
        float _uncertainty;
        JetCorrectorParameters _L1JetPar, _L2JetPar, _L3JetPar, _ResJetPar;
        JetCorrectionUncertainty* _JetUncertainty;
        JESpaths _paths;

    public:
        /**
         * @brief Construct a new Jet Recalibrator object.
         * 
         */
        JetRecalibrator();
        /**
         * @brief Construct a new Jet Recalibrator object.
         * 
         * @param jecTag The JEC tag to identify the JEC files to load.
         * @param jetType The type of jet - ex. AK8PFPuppi.
         * @param doResidualJECs Flag to turn on or off the residual JECs
         * @param uncertType Empty string for the total uncertainty but any uncertainty in the JEC file can be provided.
         * @param upToLevel Correction level to apply. Options are 1, 2, or 3 (corresponding to L1, L2, L3). Defaults to 3.
         */
        JetRecalibrator( str jecTag, str jetType, bool doResidualJECs,
                        str uncertType, int upToLevel=3
                        //  bool calculateSeparateCorrections=false,
                        //  bool calculateType1METCorrection=false,
                        //  std::map<str, float> type1METParams = {
                        //     {'jetPtThreshold', 15.},
                        //     {'skipEMfractionThreshold', 0.9},
                        //     {'skipMuons', 1} // True
                        //  }
                        );
        ~JetRecalibrator();
        /**
         * @brief Calculate the correction for a given jet and rho and store the value internally.
         * 
         * @param jet TIMBER jet struct (generated automatically by TIMBER's analyzer()) which
         *  stores the attributes of the jet (pt, eta, phi, tagging values, etc).
         * @param fixedGridRhoFastjetAll Stored in the NanoAOD with this name as the branch name.
         * @return void
         */
        template <class T>
        void CalculateCorrection(T jet, float fixedGridRhoFastjetAll){
            _JetCorrector->setJetPhi(jet.phi);
            _JetCorrector->setJetEta(jet.eta);
            _JetCorrector->setJetPt(jet.pt * (1. - jet.rawFactor));
            _JetCorrector->setJetA(jet.area);
            _JetCorrector->setRho(fixedGridRhoFastjetAll);
            _correction = _JetCorrector->getCorrection() * (1. - jet.rawFactor);
        };
        /**
         * @brief Calculate the correction uncertainty for a given jet and store the value internally.
         *  WARNING: CalculateCorrection must be run first.
         * 
         * @param jet TIMBER jet struct (generated automatically by TIMBER's analyzer()) which
         *  stores the attributes of the jet (pt, eta, phi, tagging values, etc).
         * @param delta Multiplicative factor on the uncertainty. Defaults to 1.
         */
        template <class T>
        void CalculateUncertainty(T jet, float delta = 1){
            if (delta != 0) {
                _JetUncertainty->setJetPhi(jet.phi);
                _JetUncertainty->setJetEta(jet.eta);
                _JetUncertainty->setJetPt(_correction * jet.pt);
                _uncertainty = delta*_JetUncertainty->getUncertainty(true);

            } else {
                _uncertainty = 0;
            }
        };
        /**
         * @brief Return the internally stored correction value that was calculated 
         *  during CalculateCorrection.
         * 
         * @return float 
         */
        float GetCorrection() {return _correction;};
        /**
         * @brief Return the internally stored uncertainty value that was calculated 
         *  during CalculateUncertainty.
         * 
         * @return float 
         */
        float GetUncertainty() {return _uncertainty;};
};
#endif