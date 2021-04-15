#ifndef _TIMBER_HEM_DROP
#define _TIMBER_HEM_DROP
#include "common.h"
#include <iostream>
#include <string>
#include <numeric>

using namespace Pythonic;
/**
 * @brief C++ class to weight events as if one were dropping any events with a jet
 * in the effected region. Information on the HEM15/16 issue [here](https://hypernews.cern.ch/HyperNews/CMS/get/JetMET/2000.html).
 * Note that this class is not meant to scale jet energy as described at the link. In place of
 * energy scaling, the evaluation will return 0 or 1 for data and either 0.353 or 1 for MC (affected and unaffected, respectively).
 * The value of 0.353 is derived from the ratio of 2018 affected by this issue (that is, 35.3% of MC should be unaffected but MC obviously
 * does not have run or luminosity blocks).
 */
class HEM_drop {
    private:
        bool _isAffectedData;
        bool _isDataB;
        std::vector<int> _idxToCheck;
        std::string _setname;
    public:
        /**
         * @brief Constructor for HEM_drop
         * 
         * @param setname dataA, dataB, dataC, dataD, or some MC name (does not matter what)
         * @param idxToCheck Vector of jet indexes to check. Defaults to empty in which case all jets will be checked.
         */
        HEM_drop(std::string setname, std::vector<int> idxToCheck = {});
        /**
         * @brief Return an event weight based on the existence of at least one jet in the affected HEM15/16 region.
         * The algorithm is meant to drop the event entirely in data if there is a jet in this region and to weight
         * down the event if affected in simulation.
         * @param run run for data. Defaults to 0 (to be used with MC).
         * @param FatJet_eta 
         * @param FatJet_phi  
         */
        std::vector<float> eval(RVec<float> FatJet_eta, RVec<float> FatJet_phi, int run = 0);
};
#endif