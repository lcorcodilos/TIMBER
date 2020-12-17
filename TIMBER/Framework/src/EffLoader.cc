#include <string>
#include "TFile.h"
#include "TEfficiency.h"

/**
 * @class EffLoader
 * @brief Generic histogram loader with methods to return bin values.
 */
class EffLoader {
    private:
        TFile *file;
    public:
        TEfficiency *efficiency; //!< Histogram object
        /**
         * @brief Empty constructor
         */
        EffLoader(){};
        /**
         * @brief Construct a new EffLoader object
         * 
         * @param filename File to access.
         * @param histname Histogram name in the file.
         */
        EffLoader(std::string filename, std::string histname);
        /**
         * @brief Evaluate by bin numbers.
         * 
         * @param binx 
         * @return std::vector<float> {nominal value, up error+nominal, down error+nominal}
         */
        std::vector<float> eval_bybin(int binx);
        /**
         * @brief Evaluate by axis value.
         * 
         * @param xval 
         * @return std::vector<float> {nominal value, up error+nominal, down error+nominal}
         */
        std::vector<float> eval(float xval);
            
};

EffLoader::EffLoader(std::string filename, std::string effname) {
    file = TFile::Open(filename.c_str());
    efficiency = (TEfficiency*)file->Get(effname.c_str());
}


std::vector<float> EffLoader::eval(float xval){
    int binx;
    float effval;
    float effup;
    float effdown;
    binx    = efficiency->FindFixBin(xval);
    effval  = efficiency->GetEfficiency(binx);
    effup   = effval + efficiency->GetEfficiencyErrorUp(binx);
    effdown = effval - efficiency->GetEfficiencyErrorLow(binx);
    return {effval,effup,effdown};
}

