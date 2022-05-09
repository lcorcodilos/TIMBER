#ifndef _TIMBER_JMS_WEIGHT
#define _TIMBER_JMS_WEIGHT
#include <string>
#include <cstdlib>
#include <map>
#include <vector>
#include <ROOT/RVec.hxx>

using namespace ROOT::VecOps;

/**
 * @brief C++ class to directly handle JMS weights
 *  jet substructure. The values are from AN2020/231 v8
 */
class JMS_weight {
    private:
        std::map< int, std::vector<float> > _jmsTable {
            {2016, {1.000, 1.002, 0.998 } },
            {2017, {1.002, 1.008 ,0.996 } },
            {2018, {0.994, 0.995 ,0.987 } }
        };
        std::vector<float> _jmsVals;
    public:
        /**
         * @brief Construct a new JMS weight object
         * 
         * @param year Options are 2016, 2017, or 2018.
         */
        JMS_weight(int year);
        ~JMS_weight(){};
        /**
         * @brief Evaluation just returns the scale factors for the provided year.
         *  The number of jets must be provided so that a weight for each jet can
         *  be stored correctly.
         * 
         * @param nJets The number of jets.
         * @return RVec< RVec<float>> Nested vector of floats where the outer vector
         *  is the jet index and the inner vector is the nominal (0), up (1), and down (2
         *  variations for that jet.
         */
        RVec<RVec<float>> eval(size_t nJets);
};
#endif