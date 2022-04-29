// without CMSSW / standalone:
#include "TIMBER/Framework/ext/BTagCalibrationStandalone.h"
#include "TIMBER/Framework/ext/BTagCalibrationStandalone.cpp"
#include <ROOT/RVec.hxx>

using namespace ROOT::VecOps;

/**
 * @class AK4Btag_SF
 * @brief b tagging scale factor lookup.
 */
class AK4Btag_SF {
    public:
        /**
         * @brief Construct a new b tag scale factor lookup object
         * 
         * @param year 16, 17, or 18.
         * @param tagger Ex. DeepCSV, DeepJet
         * @param op_string "loose", "medium", "tight", "reshaping"
         */
        AK4Btag_SF(std::string year, std::string tagger, std::string op_string);
        ~AK4Btag_SF(){};
        /**
         * @brief Per-event evaluation function
         * 
         * @param pt \f$p_{T}\f$ of subjet
         * @param eta \f$\eta\f$ of subjet
         * @return RVec<float> Nominal, up, down scale factor values.
         */
        RVec<float> eval(float pt, float eta,int flav, float disc);
        RVec<float> evalCollection(int nJet, RVec<float> pt, RVec<float> eta, RVec<float> flav, RVec<float> disc,int var);
    private:
        std::string csv_file;
        BTagEntry::OperatingPoint operating_point;
        BTagCalibration calib;
        BTagCalibrationReader reader;
};

AK4Btag_SF::AK4Btag_SF(std::string year, std::string tagger, std::string op_string){
		std::cout<<tagger<<" "<<year<<" "<<op_string<<"\n";
        if (op_string == "loose") {
            operating_point = BTagEntry::OP_LOOSE;
        } else if (op_string == "medium") {
            operating_point = BTagEntry::OP_MEDIUM;
        } else if (op_string == "tight") {
            operating_point = BTagEntry::OP_TIGHT;
        } else if (op_string == "reshaping") {
            operating_point = BTagEntry::OP_RESHAPING;
        }
        else{
            throw "Operating point type not supported!";
        }

        if (year == "2016APV") {
            csv_file = std::string(std::getenv("TIMBERPATH"))+"TIMBER/data/OfficialSFs/FILENAME.csv";
        } else if (year == "2016") {
            csv_file = std::string(std::getenv("TIMBERPATH"))+"TIMBER/data/OfficialSFs/FILENAME.csv";
        } else if (year == "2017") {
            csv_file = std::string(std::getenv("TIMBERPATH"))+"TIMBER/data/OfficialSFs/DeepJet_106XUL17SF_V2.csv";
        } else if (year == "2018") {
            csv_file = std::string(std::getenv("TIMBERPATH"))+"TIMBER/data/OfficialSFs/DeepJet_106XUL18SF.csv";
        }

        std::cout<<csv_file<<"\n";
        // setup calibration + reader
        calib = BTagCalibration(tagger, csv_file);
        std::cout<<"Created calib\n";
        reader = BTagCalibrationReader(operating_point,  // operating point
                                     "central",             // central sys type
                                     {"up_hf", "down_hf"});      // other sys types
        std::cout<<"Created reader\n";
        reader.load(calib,               
                    BTagEntry::FLAV_B,    
                    "iterativefit");
        reader.load(calib,
                    BTagEntry::FLAV_C,
                    "iterativefit");
        reader.load(calib,
                    BTagEntry::FLAV_UDSG,
                    "iterativefit");
        std::cout<<"Loaded reader\n";

}


RVec<float> AK4Btag_SF::eval(float pt, float eta, int flav, float disc) {
    RVec<float> jet_scalefactor(3);

    BTagEntry::JetFlavor fl = static_cast<BTagEntry::JetFlavor>(flav);

    float nom = reader.eval_auto_bounds("central", fl, eta, pt, disc);//eta, pt, discr
    //float up = reader.eval_auto_bounds("up_hf", fl, eta, pt, disc);
    //float down = reader.eval_auto_bounds("down_hf", fl, eta, pt, disc);
    float down = 0.98*nom;
    float up = 1.02*nom;

    jet_scalefactor[0] = nom;
    jet_scalefactor[1] = down;
    jet_scalefactor[2] = up;

    return jet_scalefactor;
};

RVec<float> AK4Btag_SF::evalCollection(int nJet, RVec<float> pt, RVec<float> eta, RVec<float> flav, RVec<float> disc,int var) {
    //int var 0,1,2 = nom,down,up
    //evaluate at central, apply 2% unc if var>0
    RVec<float> recalib_disc(nJet);
    BTagEntry::JetFlavor fl;
    for(int i=0; i<nJet;i++){
        if(flav[i]==5){
            fl = static_cast<BTagEntry::JetFlavor>(2);//b
        }
        else if(flav[i]==4){
            fl = static_cast<BTagEntry::JetFlavor>(1);//c
        }
        else{
            fl = static_cast<BTagEntry::JetFlavor>(0);//udsg
        }
        float sf = reader.eval_auto_bounds("central", fl, eta[i], pt[i], disc[i]);
        if(var==1){
            sf = sf*0.98;
        }
        else if(var==2){
            sf = sf * 1.02;
        }
        recalib_disc[i] = sf*disc[i];
    }

    return recalib_disc;
};