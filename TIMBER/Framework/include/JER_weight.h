#include <string>
#include <ROOT/RVec.hxx>
#include "JetSmearer.h"

using namespace ROOT::VecOps;

class JER_weight {
    private:
        JetSmearer _smearer;
    public:
        JER_weight(std::string jetType, std::string jerTag);
        ~JER_weight(){};

        template <class Tjet, class TgenJet>
        RVec< RVec<float> > eval(RVec<Tjet> jets, RVec<TgenJet> genJets){
            RVec< RVec<float> > out (jets.size());
            
            for (size_t ijet = 0; ijet < jets.size(); ijet++) {
                RVec<LorentzV> genJetsV = hardware::TLvector(genJets);
                out[ijet] = (RVec<float>)GetSmearValsPt(jets[ijet], genJetsV);
            }
            return out;
        }
};




