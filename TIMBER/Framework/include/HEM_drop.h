#include "common.h"
#include <iostream>
#include <map>
#include <numeric>

using namespace Pythonic;
/**
 * @brief Return an event weight based on the existence of at least one jet in the affected HEM15/16 region.
 * The algorithm is meant to drop the event entirely in data if there is a jet in this region and to weight
 * down the event if affected in simulation.
 * Find more on the issue [here](https://hypernews.cern.ch/HyperNews/CMS/get/JetMET/2000.html).
 * Note that this script is not meant to scale jet energy as described at the link. sIn place of
 * energy scaling, this function will return 0 or 1 for data and either 0.353 or 1 for MC (affected and unaffected, respectively).
 * The value of 0.353 is derived from the ratio of 2018 affected by this issue (that is, 35.3% of MC should be unaffected but MC obviously
 * does not have run or luminosity blocks).
 * 
 * @param setname dataA, dataB, dataC, dataD, or some MC name (does not matter what)
 * @param run run for data. Defaults to 0 (to be used with MC).
 * @param FatJet_eta 
 * @param FatJet_phi 
 * @param idxToCheck Vector of jet indexes to check. Defaults to empty in which case all jets will be checked.
 * @return float Event weight
 */
float HEM_drop(std::string setname, RVec<float> FatJet_eta, RVec<float> FatJet_phi, int run = 0, std::vector<int> idxToCheck = {});