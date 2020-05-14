// without CMSSW / standalone:
#include "HAMMER/Framework/ExternalTools/BTagCalibrationStandalone.h"
#include "HAMMER/Framework/ExternalTools/BTagCalibrationStandalone.cpp"
#include <ROOT/RVec.hxx>

using namespace ROOT::VecOps;

class SJBtag_SF {
    public:
        SJBtag_SF(int year, std::string tagger, std::string op_string);
        ~SJBtag_SF(){};
        RVec<float> eval(float pt, float eta);
    private:
        std::string csv_file;
        BTagEntry::OperatingPoint operating_point;
        BTagCalibration calib;
        BTagCalibrationReader reader;
};

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
            csv_file = "HAMMER/data/OfficialSFs/DeepCSV_2016LegacySF_V1.csv";
        } else if (year == 17) {
            csv_file = "HAMMER/data/OfficialSFs/subjet_DeepCSV_94XSF_V4_B_F.csv";
        } else if (year == 18) {
            csv_file = "HAMMER/data/OfficialSFs/DeepCSV_102XSF_V1.csv";
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
    // Note: this is for b jets, for c jets (light jets) use FLAV_C (FLAV_UDSG)
    // auto sf_lookup = [this](float eta, float pt){
    //     std::vector<float> v;

    //     v.push_back(reader.eval_auto_bounds("central", BTagEntry::FLAV_B, eta, pt));
    //     v.push_back(reader.eval_auto_bounds("up", BTagEntry::FLAV_B, eta, pt));
    //     v.push_back(reader.eval_auto_bounds("down", BTagEntry::FLAV_B, eta, pt));

    //     return v;
    // };

    // auto jet_scalefactor = Map(pt_vec, eta_vec, sf_lookup);

    RVec<float> jet_scalefactor(3);

    float nom = reader.eval_auto_bounds("central", BTagEntry::FLAV_B, eta, pt);
    float up = reader.eval_auto_bounds("up", BTagEntry::FLAV_B, eta, pt);
    float down = reader.eval_auto_bounds("down", BTagEntry::FLAV_B, eta, pt);

    jet_scalefactor[0] = nom;
    jet_scalefactor[1] = up;
    jet_scalefactor[2] = down;

    return jet_scalefactor;
};
