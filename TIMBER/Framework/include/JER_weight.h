#ifndef _TIMBER_JER_WEIGHT
#define _TIMBER_JER_WEIGHT
#include <string>
#include <ROOT/RVec.hxx>
#include "JetSmearer.h"

using namespace ROOT::VecOps;

class JER_weight {
    private:
        JetSmearer _smearer;
    public:
        JER_weight(std::string jerTag, std::string jetType);
        ~JER_weight(){};

        template <class Tjet, class TgenJet>
        RVec< RVec<float> > eval(std::vector<Tjet> jets, std::vector<TgenJet> genJets, float fixedGridRhoFastjetAll){
            RVec< RVec<float> > out (jets.size());
            for (size_t ijet = 0; ijet < jets.size(); ijet++) {
                out[ijet] = (RVec<float>)_smearer.GetSmearValsPt(hardware::TLvector(jets[ijet]), hardware::TLvector(genJets), fixedGridRhoFastjetAll);
            }
            return out;
        }
};
#endif