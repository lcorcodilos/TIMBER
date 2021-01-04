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
        TEfficiency *efficiency; //!< Histogram object
        int binx;
        int globalbin;
        float effval;
        float effup;
        float effdown;

    public:
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
         * @brief Evaluate by global bin number.
         * 
         * @param globalbin 
         * @return std::vector<float> {nominal value, up error+nominal, down error+nominal}
         */
        std::vector<float> eval_byglobal(int globalbin);
        /**
         * @brief Evaluate by per-axis bin numbers.
         * 
         * @param binx 
         * @param biny
         * @param binz 
         * @return std::vector<float> {nominal value, up error+nominal, down error+nominal}
         */
        std::vector<float> eval_bybin(int binx, int biny = 0, int binz = 0);
        /**
         * @brief Evaluate by axis value.
         * 
         * @param xval 
         * @param yval
         * @param zval
         * @return std::vector<float> {nominal value, up error+nominal, down error+nominal}
         */
        std::vector<float> eval(float xval, float yval = 0, float zval = 0);
            
};

EffLoader::EffLoader(std::string filename, std::string effname) {
    file = TFile::Open(filename.c_str());
    efficiency = (TEfficiency*)file->Get(effname.c_str());
}

std::vector<float> EffLoader::eval_byglobal(int globalbin){
    effval  = efficiency->GetEfficiency(globalbin);
    effup   = effval + efficiency->GetEfficiencyErrorUp(globalbin);
    effdown = effval - efficiency->GetEfficiencyErrorLow(globalbin);
    return {effval,effup,effdown};
}

std::vector<float> EffLoader::eval_bybin(int binx, int biny, int binz){
    globalbin = efficiency->GetGlobalBin(binx, biny, binz);
    return eval_byglobal(globalbin);
}

std::vector<float> EffLoader::eval(float xval, float yval, float zval){
    globalbin    = efficiency->FindFixBin(xval, yval, zval);
    return eval_byglobal(globalbin);
}