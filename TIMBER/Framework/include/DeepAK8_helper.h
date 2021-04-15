#ifndef _TIMBER_DEEPAK8_HELPER
#define _TIMBER_DEEPAK8_HELPER
#include <vector>
#include <map>
#include <string>
#include <fstream>
#include <iostream>
#include <cstdlib>
#include <sstream>

/**
 * @brief C++ class to access scale factors associated with DeepAK8 tagging.
 */
class DeepAK8_helper {
    private:
        std::string entry_to_find;
        std::vector<std::vector<float> > _values;
        std::string _p = std::string(std::getenv("TIMBERPATH"))+"TIMBER/data/OfficialSFs/DeepAK8V2_Top_W_SFs.csv";

    public:
        /**
         * @brief Construct a new DeepAK8_helper object
         * 
         * @param particle Either "Top" or "W"
         * @param year 
         * @param workingpoint Ex. "0p5"
         * @param massDecorr 
         */
        DeepAK8_helper(std::string particle, int year, std::string workingpoint, bool massDecorr);
        ~DeepAK8_helper(){};
        /**
         * @brief Lookup the scale factor and variations based on the AK8 jet momentum.
         * Returned values are absolute {nominal, up, down}.
         * 
         * @param pt 
         * @return std::vector<float> {nominal, up, down} (absolute)
         */
        std::vector<float> eval(float pt);
};
#endif