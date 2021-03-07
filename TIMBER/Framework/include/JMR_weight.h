#ifndef _TIMBER_JMR_WEIGHT
#define _TIMBER_JMR_WEIGHT
#include <string>
#include <ROOT/RVec.hxx>
#include <TF1.h>
#include "JetSmearer.h"

using namespace ROOT::VecOps;
// CURRENTLY ONLY SUPPORTS TAU21
class JMR_weight {
    private:
        JetSmearer _smearer;
        std::vector<float> _getJMRvals(int year);
        
    public:
        JMR_weight(int year);
        ~JMR_weight(){};

        template <class Tjet, class TgenJet>
        RVec< RVec<float> > eval(std::vector<Tjet> jets, std::vector<TgenJet> genJets){
            RVec< RVec<float> > out (jets.size());
            
            for (size_t ijet = 0; ijet < jets.size(); ijet++) {
                RVec<LorentzV> genJetsV = hardware::TLvector(genJets);
                out[ijet] = (RVec<float>)_smearer.GetSmearValsM(hardware::TLvector(jets[ijet]), hardware::TLvector(genJets));
            }
            return out;
        }
};
#endif