#ifndef _TIMBER_JER_WEIGHT
#define _TIMBER_JER_WEIGHT
#include <string>
#include <ROOT/RVec.hxx>
#include "JetSmearer.h"

using namespace ROOT::VecOps;
/**
 * @brief C++ class to handle the JER weight calculations
 */
class JER_weight {
    private:
        JetSmearer _smearer;
    public:
        /**
         * @brief Construct a new JER weight object
         * 
         * @param jerTag The JER tag to identify the JER files to load.
         * @param jetType The type of jet - ex. AK8PFPuppi
         */
        JER_weight(std::string jerTag, std::string jetType);
        ~JER_weight(){};
        /**
         * @brief Evaluation calculates the factor necessary for each jet in 
         *  the provided vector of jets* in order to smear
         *  the jet \f$p_{T}\f$ distribution. See JetSmearer
         *  for more information on the smearing algorithm.
         * 
         * @param jets Vector of structs with the jet collection branches as attributes.
         * @param genJets Vector of structs with the gen jet collection branches as attributes.
         * @param fixedGridRhoFastjetAll Stored in the NanoAOD with this name as the branch name.
         * @return RVec< RVec<float> > Nested vector of floats where the outer vector
         *  is the jet index and the inner vector is the nominal (0), up (1), and down (2
         *  variations for that jet.
         */
        template <class Tjet, class TgenJet>
        RVec<RVec<float>> eval(std::vector<Tjet> jets, std::vector<TgenJet> genJets, float fixedGridRhoFastjetAll){
            RVec< RVec<float> > out (jets.size());
            for (size_t ijet = 0; ijet < jets.size(); ijet++) {
                out[ijet] = (RVec<float>)_smearer.GetSmearValsPt(hardware::TLvector(jets[ijet]), hardware::TLvector(genJets), fixedGridRhoFastjetAll);
            }
            return out;
        }
};
#endif