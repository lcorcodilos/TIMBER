// without CMSSW / standalone:
#include "../ExternalTools/BTagCalibrationStandalone.h"
#include "../ExternalTools/BTagCalibrationStandalone.cpp"
#include <ROOT/RVec.hxx>

using namespace ROOT::VecOps;

class Btag_SF {
    public:
        Btag_SF(int year, std::string tagger, std::string op_string);
        ~Btag_SF();
        RVec<std::vector<float, std::allocator<float> > > eval(RVec<float> pt_vec, RVec<float> eta_vec);
    private:
        std::string csv_file;
        BTagEntry::OperatingPoint operating_point;
        BTagCalibration calib;
        BTagCalibrationReader reader;
};

Btag_SF::Btag_SF(int year, std::string tagger, std::string op_string) {
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
    

RVec<std::vector<float, std::allocator<float> > > Btag_SF::eval(RVec<float> pt_vec, RVec<float> eta_vec) {
    std::cout << typeid(reader).name();

    // Note: this is for b jets, for c jets (light jets) use FLAV_C (FLAV_UDSG)
    auto sf_lookup = [this](float eta, float pt){
        std::vector<float> v;

        v.push_back(reader.eval_auto_bounds("central", BTagEntry::FLAV_B, eta, pt));
        v.push_back(reader.eval_auto_bounds("up", BTagEntry::FLAV_B, eta, pt));
        v.push_back(reader.eval_auto_bounds("down", BTagEntry::FLAV_B, eta, pt));

        return v;
    };

    auto jet_scalefactor = Map(pt_vec, eta_vec, sf_lookup);

    return jet_scalefactor;
};
