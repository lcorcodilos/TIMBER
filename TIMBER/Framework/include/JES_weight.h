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
/**
 * @brief C++ class to handle the JES/JEC weight calculations
 */
class JES_weight {
    private:
        const std::string _jecTag, _jetType, _uncertType;
        const bool _redoJECs;
        JetRecalibrator _jetRecalib;
        bool check_type_exists();
        std::vector<std::string> get_sources();

    public:
        /**
         * @brief Construct a new JES weight object
         * 
         * @param jecTag The JEC tag to identify the JEC files to load.
         * @param jetType The type of jet - ex. AK8PFPuppi.
         * @param uncertType Empty string for the total uncertainty but any
         *  uncertainty in the JEC file can be provided. Default is empty string.
         * @param redoJECs Set to false if the sample already has the desired JECs
         *  applied. If true, derive correction that undoes the current JECs and applies
         *  new ones instead. Uncertainty variations are calculated in either case. Defaults to false.
         */
        JES_weight(str jecTag, str jetType, str uncertType = "", bool redoJECs=false);
        ~JES_weight(){};
        /**
         * @brief If redoJECs is true, evaluation calculates the weight necessary to 
         *  uncorrect and recorrect the jet energy for each jet in the provided
         *  vector of jets*. In either case of redoJECs, the uncertainties are calculated.
         *  See JetRecalibrator for more information on the algorithm.
         * 
         * * NOTE that the "jet" is a struct which is custom made by TIMBER's analyzer()
         *  to have the branches of the collection as the attributes of the struct. To use
         *  it in TIMBER, just reference the vector of all struct of objections
         *  named `<CollectionName>s` (ex. `FatJets`).
         * 
         * @param jets Vector of structs with the jet collection branches as attributes.
         * @param fixedGridRhoFastjetAll Stored in the NanoAOD with this name as the branch name.
         * @return RVec< RVec<float> > Nested vector of floats where the outer vector
         *  is the jet index and the inner vector is the nominal (0), up (1), and down (2
         *  variations for that jet.
         */
        template <class T>
        RVec<RVec<float>> eval(std::vector<T> jets, float fixedGridRhoFastjetAll){
            RVec<RVec<float>> out (jets.size());

            for (size_t ijet = 0; ijet < jets.size(); ijet++) {
                RVec<float> ijet_out {1.0, 1.0, 1.0};
            
                if (_redoJECs) {
                    _jetRecalib.CalculateCorrection(jets[ijet], fixedGridRhoFastjetAll);
                    _jetRecalib.CalculateUncertainty(jets[ijet]);

                    ijet_out[0] = _jetRecalib.GetCorrection();
                    ijet_out[1] = _jetRecalib.GetCorrection()*(1+_jetRecalib.GetUncertainty());
                    ijet_out[2] = _jetRecalib.GetCorrection()*(1-_jetRecalib.GetUncertainty());
                } else {
                    _jetRecalib.CalculateUncertainty(jets[ijet], fixedGridRhoFastjetAll);
                    ijet_out[1] = 1+_jetRecalib.GetUncertainty();
                    ijet_out[2] = 1-_jetRecalib.GetUncertainty();
                }
                out[ijet] = ijet_out;
            }
            return out;
        };
};
#endif