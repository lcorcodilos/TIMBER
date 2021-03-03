#ifndef _TIMBER_JMS_WEIGHT
#define _TIMBER_JMS_WEIGHT
#include <string>
#include <cstdlib>
#include <map>
#include <vector>
#include <ROOT/RVec.hxx>

using namespace ROOT::VecOps;

// CURRENTLY ONLY SUPPORTS TAU21
class JMS_weight {
    private:
        std::map< int, std::vector<float> > _jmsTable {
            {2016, {1.000, 1.0094, 0.9906} },
            {2017, {0.982, 0.986 , 0.978 } },
            {2018, {0.982, 0.986 , 0.978 } }
        };
        std::vector<float> _jmsVals;
    public:
        JMS_weight(int year);
        ~JMS_weight(){};
        RVec< RVec<float>> eval(size_t nJets);
};
#endif