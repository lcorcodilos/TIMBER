#ifndef _TIMBER_SJBTAG_SF
#define _TIMBER_SJBTAG_SF
// without CMSSW / standalone:
#include "../ext/BTagCalibrationStandalone.h"
#include <ROOT/RVec.hxx>

using namespace ROOT::VecOps;

/**
 * @class SJBtag_SF
 * @brief C++ class. Subjet b tagging scale factor lookup.
 */
class SJBtag_SF {
    private:
        std::string csv_file;
        BTagEntry::OperatingPoint operating_point;
        BTagCalibration calib;
        BTagCalibrationReader reader;

    public:
        /**
         * @brief Construct a new subjet b tag scale factor lookup object
         * 
         * @param year 16, 17, or 18.
         * @param tagger Ex. DeepCSV. See TIMBER/data/OfficialSFs/ for others.
         * @param op_string "loose", "medium", "tight"
         */
        SJBtag_SF(int year, std::string tagger, std::string op_string);
        ~SJBtag_SF(){};
        /**
         * @brief Per-event evaluation function
         * 
         * @param pt \f$p_{T}\f$ of subjet
         * @param eta \f$\eta\f$ of subjet
         * @return RVec<float> Nominal, up, down scale factor values.
         */
        RVec<float> eval(float pt, float eta);
};
#endif