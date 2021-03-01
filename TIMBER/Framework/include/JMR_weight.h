#include <string>
#include <ROOT/RVec.hxx>
#include <TF1.h>
#include "JetSmearer.h"

using namespace ROOT::VecOps;
// CURRENTLY ONLY SUPPORTS TAU21
class JMR_weight {
    private:
        JetSmearer _smearer;
        std::map< int, std::vector<float> > _jmrTable {
            {2016, {1.00, 1.2,  0.8 } },
            {2017, {1.09, 1.14, 1.04} },
            {2018, {1.09, 1.14, 1.04} }
        };
        
    public:
        JMR_weight(int year);
        ~JMR_weight(){};

        template <class Tjet, class TgenJet>
        RVec< RVec<float> > eval(RVec<Tjet> jets, RVec<TgenJet> genJets){
            RVec< RVec<float> > out (jets.size());
            
            for (size_t ijet = 0; ijet < jets.size(); ijet++) {
                RVec<LorentzV> genJetsV = hardware::TLvector(genJets);
                out[ijet] = (RVec<float>)GetSmearValsM(jets[ijet], genJetsV);
            }
            return out;
        }
};