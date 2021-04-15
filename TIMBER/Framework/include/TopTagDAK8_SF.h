#ifndef _TIMBER_TOPTAGDAK8_SF
#define _TIMBER_TOPTAGDAK8_SF
#include "DeepAK8_helper.h"

/**
 * @brief C++ class to access scale factors associated with DeepAK8 top tagging.
 */
class TopTagDAK8_SF {
    private:
        DeepAK8_helper helper;

    public:
        /**
         * @brief Construct a new TopTagDAK8_SF object
         * 
         * @param year 
         * @param workingpoint Ex. "0p5"
         * @param massDecorr 
         */
        TopTagDAK8_SF(int year, std::string workingpoint, bool massDecorr);
        ~TopTagDAK8_SF(){};
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