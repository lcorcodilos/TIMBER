#include "../include/SJBtag_SF.h"

SJBtag_SF::SJBtag_SF(int year, std::string tagger, std::string op_string) {
    if (op_string == "loose") {
        operating_point = BTagEntry::OP_LOOSE;
    } else if (op_string == "medium") {
        operating_point = BTagEntry::OP_MEDIUM;
    } else if (op_string == "tight") {
        operating_point = BTagEntry::OP_TIGHT;
    } else {
        throw "Operating point type not supported!";
    }

    
    if (year == 16) {
        csv_file = std::string(std::getenv("TIMBERPATH"))+"TIMBER/data/OfficialSFs/DeepCSV_2016LegacySF_V1.csv";
    } else if (year == 17) {
        csv_file = std::string(std::getenv("TIMBERPATH"))+"TIMBER/data/OfficialSFs/subjet_DeepCSV_94XSF_V4_B_F.csv";
    } else if (year == 18) {
        csv_file = std::string(std::getenv("TIMBERPATH"))+"TIMBER/data/OfficialSFs/DeepCSV_102XSF_V1.csv";
    }

    // setup calibration + reader
    calib = BTagCalibration(tagger, csv_file);
    reader = BTagCalibrationReader(operating_point,  // operating point
                                    "central",             // central sys type
                                    {"up", "down"});      // other sys types

    reader.load(calib,                // calibration instance
                BTagEntry::FLAV_B,    // btag flavour
                "comb");               // measurement type

}; 

RVec<float> SJBtag_SF::eval(float pt, float eta) {
    RVec<float> jet_scalefactor(3);

    float nom = reader.eval_auto_bounds("central", BTagEntry::FLAV_B, eta, pt);
    float up = reader.eval_auto_bounds("up", BTagEntry::FLAV_B, eta, pt);
    float down = reader.eval_auto_bounds("down", BTagEntry::FLAV_B, eta, pt);

    jet_scalefactor[0] = nom;
    jet_scalefactor[1] = up;
    jet_scalefactor[2] = down;

    return jet_scalefactor;
};
