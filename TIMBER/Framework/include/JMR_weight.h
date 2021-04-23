#ifndef _TIMBER_JMR_WEIGHT
#define _TIMBER_JMR_WEIGHT
#include <string>
#include <ROOT/RVec.hxx>
#include <TF1.h>
#include "JetSmearer.h"

using namespace ROOT::VecOps;
/**
 * @brief C++ class to directly handle JMR weights in the case of tau21
 * jet substructure. The values used (nominal, up, down) are:
 *  - 2016: 1.00, 1.2,  0.8
 *  - 2017: 1.09, 1.14, 1.04
 *  - 2018: 1.09, 1.14, 1.04
 */
class JMR_weight {
    private:
        std::map< int, std::vector<float> > _jmrTable {
            {2016, {1.00, 1.2,  0.8 } },
            {2017, {1.09, 1.14, 1.04} },
            {2018, {1.09, 1.14, 1.04} }
        };
        JetSmearer _smearer;
        
    public:
        /**
         * @brief Construct a new JMR weight object
         * 
         * @param year Options are 2016, 2017, or 2018.
         */
        JMR_weight(int year);
        ~JMR_weight(){};
        /**
         * @brief Evaluation calculates the factor necessary for each jet in 
         *  the provided vector of jets* in order to smear
         *  the jet mass distribution. See JetSmearer
         *  for more information on the smearing algorithm.
         * 
         * * NOTE that the "jet" is a struct which is custom made by TIMBER's analyzer()
         *  to have the branches of the collection as the attributes of the struct. To use
         *  it in TIMBER, just reference the vector of all struct of objections
         *  named `<CollectionName>s` (ex. `FatJets`).
         * 
         * @param jets Vector of structs with the jet collection branches as attributes.
         * @param genJets Vector of structs with the gen jet collection branches as attributes.
         * @return RVec< RVec<float> > Nested vector of floats where the outer vector
         *  is the jet index and the inner vector is the nominal (0), up (1), and down (2
         *  variations for that jet.
         */
        template <class Tjet, class TgenJet>
        RVec<RVec<float>> eval(std::vector<Tjet> jets, std::vector<TgenJet> genJets){
            RVec<RVec<float>> out (jets.size());
            
            for (size_t ijet = 0; ijet < jets.size(); ijet++) {
                RVec<LorentzV> genJetsV = hardware::TLvector(genJets);
                out[ijet] = (RVec<float>)_smearer.GetSmearValsM(hardware::TLvector(jets[ijet]), hardware::TLvector(genJets));
            }
            return out;
        }
};
#endif